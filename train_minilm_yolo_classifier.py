"""
Resume Classifier — Single Unified Pipeline
============================================
Architecture:
  [Resume Text / PDF]
        ↓
  ┌─────────────────────────────────────────────────┐
  │  FROZEN Pretrained Encoder (anass1209/           │
  │  resume-job-matcher-all-MiniLM-L6-v2)           │
  │  → 384-dim semantic embedding                   │
  └─────────────────────────────────────────────────┘
        ↓
  ┌─────────────────────────────────────────────────┐
  │  YOLO-Head Classifier (single-shot MLP)         │
  │  FC(384→512) → BN → SiLU → Dropout             │
  │  FC(512→256) → BN → SiLU → Dropout             │
  │  FC(256→128) → BN → SiLU                       │
  │  FC(128→24)  → Softmax → Category Label        │
  └─────────────────────────────────────────────────┘

Usage:
  python train_minilm_yolo_classifier.py --epochs 30
  python train_minilm_yolo_classifier.py --epochs 30 --finetune   # fine-tune encoder too
"""

import re
import sys
import json
import time
import joblib
import argparse
import numpy as np
import pandas as pd
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("ERROR: sentence-transformers not installed.")
    print("Run: pip install sentence-transformers")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────
PRETRAINED_MODEL_ID = "anass1209/resume-job-matcher-all-MiniLM-L6-v2"
EMBED_DIM           = 384        # MiniLM-L6-v2 output dimension
SEED                = 42
BATCH_SIZE          = 32
CSV_PATH            = Path("archive123/Resume/Resume.csv")
OUTPUT_DIR          = Path("runs/resume_minilm_yolo")

torch.manual_seed(SEED)
np.random.seed(SEED)


# ─────────────────────────────────────────────────────────────────────────────
# Text pre-processor
# ─────────────────────────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ─────────────────────────────────────────────────────────────────────────────
# Dataset — works with pre-computed embeddings (fast) or raw text (fine-tune)
# ─────────────────────────────────────────────────────────────────────────────
class EmbeddingDataset(Dataset):
    def __init__(self, embeddings: np.ndarray, labels: np.ndarray):
        self.X = torch.tensor(embeddings, dtype=torch.float32)
        self.y = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


# ─────────────────────────────────────────────────────────────────────────────
# YOLO-Head Classifier  (single-shot, inspired by YOLO detection head)
# ─────────────────────────────────────────────────────────────────────────────
class YOLOHeadClassifier(nn.Module):
    """
    Single-shot classification head — replicates YOLO's philosophy of a
    compact, dense head that fires once per input.
    Uses SiLU (Swish) activation — same as YOLOv11 backbone.
    """
    def __init__(self, input_dim: int, num_classes: int, dropout: float = 0.3):
        super().__init__()
        self.head = nn.Sequential(
            # Layer 1: 384 → 512
            nn.Linear(input_dim, 512),
            nn.BatchNorm1d(512),
            nn.SiLU(),                     # YOLOv11 uses SiLU throughout
            nn.Dropout(dropout),

            # Layer 2: 512 → 256
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.SiLU(),
            nn.Dropout(dropout),

            # Layer 3: 256 → 128
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.SiLU(),
            nn.Dropout(0.1),

            # Output: 128 → num_classes  (single-shot prediction)
            nn.Linear(128, num_classes),
        )
        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(x)


# ─────────────────────────────────────────────────────────────────────────────
# Full unified model  ( MiniLM encoder  +  YOLO-Head )
# ─────────────────────────────────────────────────────────────────────────────
class MiniLMYOLOModel(nn.Module):
    """
    End-to-end model: MiniLM encoder (frozen) + YOLO-Head classifier.
    Pass raw text in predict(); head-only forward() expects pre-embedded tensors.
    """
    def __init__(self, encoder: SentenceTransformer, num_classes: int,
                 finetune_encoder: bool = False):
        super().__init__()
        self.encoder          = encoder
        self.finetune_encoder = finetune_encoder
        self.yolo_head        = YOLOHeadClassifier(EMBED_DIM, num_classes)

        if not finetune_encoder:
            for param in self.encoder.parameters():
                param.requires_grad = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: pre-computed embedding tensor [B, 384]"""
        return self.yolo_head(x)

    @torch.no_grad()
    def predict(self, texts: list[str], device: str = "cpu") -> np.ndarray:
        """End-to-end: raw text → class indices"""
        embeddings = self.encoder.encode(texts, convert_to_tensor=True,
                                         show_progress_bar=False)
        embeddings = embeddings.to(device)
        logits     = self.yolo_head(embeddings)
        return torch.argmax(logits, dim=1).cpu().numpy()

    @torch.no_grad()
    def predict_proba(self, texts: list[str], device: str = "cpu") -> np.ndarray:
        """End-to-end: raw text → probability array [N, num_classes]"""
        embeddings = self.encoder.encode(texts, convert_to_tensor=True,
                                         show_progress_bar=False)
        embeddings = embeddings.to(device)
        probs      = torch.softmax(self.yolo_head(embeddings), dim=1)
        return probs.cpu().numpy()


# ─────────────────────────────────────────────────────────────────────────────
# Training loop
# ─────────────────────────────────────────────────────────────────────────────
def train(args):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("=" * 65)
    print("  MiniLM + YOLO-Head Resume Classifier — Unified Pipeline")
    print("=" * 65)
    print(f"  Encoder   : {PRETRAINED_MODEL_ID}")
    print(f"  Head      : YOLO-Head (SiLU, BN, Dropout, single-shot)")
    print(f"  Device    : {device}")
    print(f"  Epochs    : {args.epochs}")
    print(f"  Fine-tune : {args.finetune}")
    print("=" * 65)

    # ── Load dataset ──────────────────────────────────────────────────────────
    print("\n[1/5] Loading dataset …")
    df = pd.read_csv(CSV_PATH)
    df["clean"] = df["Resume_str"].apply(clean_text)
    print(f"      {len(df)} resumes, {df['Category'].nunique()} categories")

    label_enc = LabelEncoder()
    df["label"] = label_enc.fit_transform(df["Category"])
    classes     = list(label_enc.classes_)
    num_classes = len(classes)

    # ── Load pretrained MiniLM encoder ───────────────────────────────────────
    print(f"\n[2/5] Loading pretrained encoder: {PRETRAINED_MODEL_ID} …")
    encoder = SentenceTransformer(PRETRAINED_MODEL_ID)

    # ── Embed entire corpus once (fast — frozen encoder) ─────────────────────
    cache_path = OUTPUT_DIR / "embeddings_cache.npy"
    if cache_path.exists() and not args.no_cache:
        print("[2/5] Loading cached embeddings …")
        embeddings = np.load(str(cache_path))
    else:
        print("[2/5] Encoding all resumes (this takes a minute on CPU) …")
        t0 = time.time()
        embeddings = encoder.encode(
            df["clean"].tolist(),
            batch_size=64,
            show_progress_bar=True,
            convert_to_numpy=True,
        )
        np.save(str(cache_path), embeddings)
        print(f"      Encoded {len(embeddings)} resumes in {time.time()-t0:.1f}s")
        print(f"      Embedding shape: {embeddings.shape}")   # (2484, 384)

    # ── Train/Val split ───────────────────────────────────────────────────────
    print("\n[3/5] Splitting dataset …")
    labels = df["label"].values
    X_tr, X_val, y_tr, y_val = train_test_split(
        embeddings, labels, test_size=0.2, random_state=SEED, stratify=labels
    )
    print(f"      Train: {len(y_tr)} | Val: {len(y_val)}")

    train_ds  = EmbeddingDataset(X_tr, y_tr)
    val_ds    = EmbeddingDataset(X_val, y_val)
    train_dl  = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  num_workers=0)
    val_dl    = DataLoader(val_ds,   batch_size=64,         shuffle=False, num_workers=0)

    # ── Build unified model ───────────────────────────────────────────────────
    print("\n[4/5] Building MiniLM + YOLO-Head model …")
    model = MiniLMYOLOModel(encoder, num_classes, finetune_encoder=args.finetune)
    model.to(device)

    yolo_params = list(model.yolo_head.parameters())
    if args.finetune:
        enc_params = [p for p in model.encoder.parameters() if p.requires_grad]
        optimizer  = torch.optim.AdamW([
            {"params": enc_params,  "lr": 2e-5, "weight_decay": 1e-4},
            {"params": yolo_params, "lr": 1e-3, "weight_decay": 1e-4},
        ])
    else:
        optimizer = torch.optim.AdamW(yolo_params, lr=1e-3, weight_decay=1e-4)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.05)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    # ── Training loop ─────────────────────────────────────────────────────────
    print(f"\n[5/5] Training for {args.epochs} epochs …\n")
    header = f"{'Epoch':<8}{'Train Loss':<13}{'Train Acc%':<13}{'Val Loss':<13}{'Val Acc%':<13}"
    print("-" * 60)
    print(header)
    print("-" * 60)

    best_val_acc = 0.0
    history      = []

    for epoch in range(1, args.epochs + 1):
        # ---- Train ----
        model.train()
        tot_loss, correct, total = 0.0, 0, 0
        for Xb, yb in train_dl:
            Xb, yb = Xb.to(device), yb.to(device)
            optimizer.zero_grad()
            out  = model.yolo_head(Xb)
            loss = criterion(out, yb)
            loss.backward()
            nn.utils.clip_grad_norm_(model.yolo_head.parameters(), max_norm=1.0)
            optimizer.step()
            tot_loss += loss.item() * len(yb)
            correct  += (out.argmax(1) == yb).sum().item()
            total    += len(yb)
        scheduler.step()
        tr_loss = tot_loss / total
        tr_acc  = correct  / total * 100

        # ---- Validate ----
        model.eval()
        v_loss, v_correct, v_total = 0.0, 0, 0
        all_preds, all_true = [], []
        with torch.no_grad():
            for Xb, yb in val_dl:
                Xb, yb = Xb.to(device), yb.to(device)
                out  = model.yolo_head(Xb)
                loss = criterion(out, yb)
                v_loss    += loss.item() * len(yb)
                v_correct += (out.argmax(1) == yb).sum().item()
                v_total   += len(yb)
                all_preds.extend(out.argmax(1).cpu().tolist())
                all_true.extend(yb.cpu().tolist())
        val_loss = v_loss    / v_total
        val_acc  = v_correct / v_total * 100

        is_best = val_acc > best_val_acc
        if is_best:
            best_val_acc = val_acc
            torch.save(model.yolo_head.state_dict(),
                       OUTPUT_DIR / "best_yolo_head.pt")

        marker = " ★" if is_best else ""
        print(f"{epoch:<8}{tr_loss:<13.4f}{tr_acc:<13.2f}{val_loss:<13.4f}{val_acc:<13.2f}{marker}")

        history.append(dict(epoch=epoch, train_loss=tr_loss, train_acc=tr_acc,
                            val_loss=val_loss, val_acc=val_acc))

    # ── Save all artefacts ────────────────────────────────────────────────────
    torch.save(model.yolo_head.state_dict(), OUTPUT_DIR / "final_yolo_head.pt")

    model_meta = {
        "encoder_id"  : PRETRAINED_MODEL_ID,
        "embed_dim"   : EMBED_DIM,
        "num_classes" : num_classes,
        "classes"     : classes,
        "epochs"      : args.epochs,
        "best_val_acc": round(best_val_acc, 4),
    }
    with open(OUTPUT_DIR / "model_meta.json", "w") as f:
        json.dump(model_meta, f, indent=2)

    pd.DataFrame(history).to_csv(OUTPUT_DIR / "training_history.csv", index=False)

    # ── Final report on best model ────────────────────────────────────────────
    model.yolo_head.load_state_dict(
        torch.load(OUTPUT_DIR / "best_yolo_head.pt", map_location=device)
    )
    model.eval()
    all_p, all_t = [], []
    with torch.no_grad():
        for Xb, yb in val_dl:
            Xb = Xb.to(device)
            all_p.extend(model.yolo_head(Xb).argmax(1).cpu().tolist())
            all_t.extend(yb.tolist())

    report = classification_report(all_t, all_p, target_names=classes, digits=4)
    print("\n" + "=" * 65)
    print(f"  Training complete!  Peak Validation Accuracy: {best_val_acc:.2f}%")
    print("=" * 65)
    print("\nFinal Classification Report (best model):")
    print(report)

    with open(OUTPUT_DIR / "classification_report.txt", "w") as f:
        f.write(report)

    print(f"\n  Artefacts saved to: {OUTPUT_DIR}/")
    print(f"    best_yolo_head.pt        — YOLO-Head weights")
    print(f"    final_yolo_head.pt       — last-epoch weights")
    print(f"    model_meta.json          — config + class names")
    print(f"    training_history.csv     — epoch metrics")
    print(f"    classification_report.txt")
    print(f"    embeddings_cache.npy     — pre-computed MiniLM embeddings")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="MiniLM + YOLO-Head Resume Classifier")
    p.add_argument("--epochs",    type=int,  default=30,
                   help="Training epochs (default: 30)")
    p.add_argument("--finetune",  action="store_true",
                   help="Also fine-tune the MiniLM encoder (slower)")
    p.add_argument("--no-cache",  action="store_true",
                   help="Re-encode even if embeddings_cache.npy exists")
    return p.parse_args()


if __name__ == "__main__":
    train(parse_args())
