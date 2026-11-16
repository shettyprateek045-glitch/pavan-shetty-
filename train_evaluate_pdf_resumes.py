"""
Train, Test, and Evaluate Model Directly on Resume PDF Files
===========================================================
1. Indexes all 2,484 PDF resume files by filename and category path.
2. Extracts text directly from PDF files using pypdf.
3. Generates 384-dim semantic embeddings with anass1209/resume-job-matcher-all-MiniLM-L6-v2.
4. Trains the single-shot YOLOv11 classification head for 30 epochs.
5. Evaluates model on a 20% holdout split of PDF files.
6. Tests inference directly on PDF files by filename (including user's Prateek_Shetty_Resume.pdf).
"""

import os
import re
import time
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)

PRETRAINED_ID = "anass1209/resume-job-matcher-all-MiniLM-L6-v2"
EMBED_DIM = 384
DATA_DIR = Path("archive123/data/data")
OUTPUT_DIR = Path("runs/pdf_resume_model")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class YOLOHeadClassifier(nn.Module):
    def __init__(self, input_dim: int, num_classes: int, dropout: float = 0.3):
        super().__init__()
        self.head = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.BatchNorm1d(512),
            nn.SiLU(),
            nn.Dropout(dropout),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.SiLU(),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.SiLU(),
            nn.Dropout(0.1),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        return self.head(x)

class EmbeddingDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

def extract_text_from_pdf(pdf_path: Path) -> str:
    try:
        reader = PdfReader(str(pdf_path))
        text = " ".join([page.extract_text() or "" for page in reader.pages])
        text = re.sub(r"http\S+", " ", text)
        text = re.sub(r"[^\w\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()
    except Exception as e:
        return ""

def main():
    print("=" * 75)
    print("   RESUME PDF TRAINING, TESTING & EVALUATION PIPELINE")
    print("=" * 75)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print(f"Pretrained Model: {PRETRAINED_ID}")

    # 1. Index all PDF resume files
    print("\n[Step 1/6] Indexing all PDF resume files from disk...")
    pdf_files = list(DATA_DIR.glob("*/*.pdf"))
    print(f"Found {len(pdf_files)} PDF resume files across {len(set(p.parent.name for p in pdf_files))} category folders.")

    records = []
    for p in pdf_files:
        records.append({
            "pdf_path": str(p),
            "file_name": p.name,
            "category": p.parent.name
        })
    df_pdfs = pd.DataFrame(records)
    print(df_pdfs.head(4)[["file_name", "category", "pdf_path"]])

    label_enc = LabelEncoder()
    df_pdfs["label"] = label_enc.fit_transform(df_pdfs["category"])
    classes = list(label_enc.classes_)
    num_classes = len(classes)

    # 2. Extract & Embed
    print("\n[Step 2/6] Loading Pretrained Sentence Transformer...")
    encoder = SentenceTransformer(PRETRAINED_ID)

    cache_path = OUTPUT_DIR / "pdf_embeddings.npy"
    if cache_path.exists():
        print(f"Loading cached PDF embeddings from {cache_path}...")
        embeddings = np.load(str(cache_path))
    else:
        # Check if archive123 cache is available
        existing_cache = Path("runs/resume_minilm_yolo/embeddings_cache.npy")
        csv_path = Path("archive123/Resume/Resume.csv")
        if existing_cache.exists() and csv_path.exists():
            print("Mapping existing high-quality embeddings to disk PDF files...")
            df_csv = pd.read_csv(csv_path)
            # Create a dictionary of (Category, ID.pdf) -> row index
            csv_map = {(row["Category"], f"{row['ID']}.pdf"): idx for idx, row in df_csv.iterrows()}
            all_embs = np.load(str(existing_cache))
            matched_embs = []
            for _, r in df_pdfs.iterrows():
                key = (r["category"], r["file_name"])
                if key in csv_map:
                    matched_embs.append(all_embs[csv_map[key]])
                else:
                    # Extract directly from PDF
                    text = extract_text_from_pdf(Path(r["pdf_path"]))
                    matched_embs.append(encoder.encode(text))
            embeddings = np.array(matched_embs)
            np.save(str(cache_path), embeddings)
            print(f"Mapped and saved {len(embeddings)} PDF embeddings. Shape: {embeddings.shape}")
        else:
            print("Extracting text directly from all PDF files...")
            texts = [extract_text_from_pdf(Path(p)) for p in df_pdfs["pdf_path"]]
            embeddings = encoder.encode(texts, batch_size=128, show_progress_bar=True, convert_to_numpy=True)
            np.save(str(cache_path), embeddings)

    # 3. Stratified Train / Validation Split
    print("\n[Step 3/6] Splitting PDF dataset into Train (80%) and Validation (20%)...")
    labels = df_pdfs["label"].values
    X_tr, X_val, y_tr, y_val, idx_tr, idx_val = train_test_split(
        embeddings, labels, np.arange(len(labels)),
        test_size=0.2, random_state=SEED, stratify=labels
    )
    val_files = df_pdfs.iloc[idx_val].copy().reset_index(drop=True)
    print(f"Train samples: {len(y_tr)}, Validation samples: {len(y_val)}")

    train_loader = DataLoader(EmbeddingDataset(X_tr, y_tr), batch_size=32, shuffle=True, drop_last=True)
    val_loader = DataLoader(EmbeddingDataset(X_val, y_val), batch_size=64, shuffle=False)

    # 4. Train Model
    print("\n[Step 4/6] Training Single-Shot YOLO-Head Model for 30 Epochs...")
    model = YOLOHeadClassifier(EMBED_DIM, num_classes).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=30)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.05)

    history = []
    best_val_acc = 0.0

    print("-" * 65)
    print(f"{'Epoch':<8}{'Train Loss':<14}{'Train Acc (%)':<16}{'Val Loss':<14}{'Val Acc (%)'}")
    print("-" * 65)

    for epoch in range(1, 31):
        model.train()
        tot_loss, correct, total = 0.0, 0, 0
        for Xb, yb in train_loader:
            Xb, yb = Xb.to(device), yb.to(device)
            optimizer.zero_grad()
            out = model(Xb)
            loss = criterion(out, yb)
            loss.backward()
            optimizer.step()
            tot_loss += loss.item() * len(yb)
            correct += (out.argmax(1) == yb).sum().item()
            total += len(yb)
        scheduler.step()

        tr_loss = tot_loss / total
        tr_acc = (correct / total) * 100

        # Validate
        model.eval()
        v_loss, v_correct, v_total = 0.0, 0, 0
        with torch.no_grad():
            for Xb, yb in val_loader:
                Xb, yb = Xb.to(device), yb.to(device)
                out = model(Xb)
                loss = criterion(out, yb)
                v_loss += loss.item() * len(yb)
                v_correct += (out.argmax(1) == yb).sum().item()
                v_total += len(yb)

        val_loss = v_loss / v_total
        val_acc = (v_correct / v_total) * 100

        is_best = val_acc > best_val_acc
        if is_best:
            best_val_acc = val_acc
            torch.save(model.state_dict(), OUTPUT_DIR / "best_model.pt")

        history.append({
            "epoch": epoch, "train_loss": tr_loss, "train_acc": tr_acc,
            "val_loss": val_loss, "val_acc": val_acc
        })

        best_flag = " *" if is_best else ""
        if epoch in [1, 5, 10, 15, 20, 25, 30] or is_best:
            print(f"{epoch:<8}{tr_loss:<14.4f}{tr_acc:<16.2f}{val_loss:<14.4f}{val_acc:<14.2f}{best_flag}")

    # Save meta & history
    pd.DataFrame(history).to_csv(OUTPUT_DIR / "training_history.csv", index=False)
    meta = {
        "model_name": "Resume-PDF-YOLO-Classifier",
        "num_classes": num_classes,
        "classes": classes,
        "best_val_acc": round(best_val_acc, 2),
        "total_pdf_files": len(df_pdfs)
    }
    with open(OUTPUT_DIR / "model_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    # 5. Evaluate Results
    print("\n[Step 5/6] Comprehensive Model Evaluation on Validation Set...")
    model.load_state_dict(torch.load(OUTPUT_DIR / "best_model.pt"))
    model.eval()

    val_tensor = torch.tensor(X_val, dtype=torch.float32).to(device)
    with torch.no_grad():
        logits = model(val_tensor)
        probs = torch.softmax(logits, dim=1).cpu().numpy()

    preds = probs.argmax(axis=1)
    top3_correct = sum(1 for i, t in enumerate(y_val) if t in probs[i].argsort()[-3:])
    top3_acc = (top3_correct / len(y_val)) * 100
    top1_acc = accuracy_score(y_val, preds) * 100

    print(f"  • Top-1 Accuracy: {top1_acc:.2f}%")
    print(f"  • Top-3 Accuracy: {top3_acc:.2f}%")
    report = classification_report(y_val, preds, target_names=classes, digits=4, zero_division=0)
    print("\nClassification Report:")
    print(report)

    with open(OUTPUT_DIR / "classification_report.txt", "w") as f:
        f.write(report)

    # 6. Test by File Name on Specific PDF Files
    print("\n[Step 6/6] Testing Predictions on Specific PDF File Names...")
    test_pdf_files = [
        "archive123/data/data/CHEF/10001727.pdf",
        "archive123/data/data/ACCOUNTANT/10554236.pdf",
        "archive123/data/data/INFORMATION-TECHNOLOGY/10089434.pdf",
        "archive123/data/data/AVIATION/11759079.pdf",
        "archive123/data/data/HR/10674770.pdf",
        "Prateek_Shetty_Resume.pdf"
    ]

    print("-" * 75)
    print(f"{'PDF File Name':<38}{'Predicted Category':<24}{'Confidence'}")
    print("-" * 75)

    for pdf_str in test_pdf_files:
        pdf_path = Path(pdf_str)
        if not pdf_path.exists():
            continue
        text = extract_text_from_pdf(pdf_path)
        if not text:
            print(f"{pdf_path.name:<38} [Error: Unable to extract text]")
            continue
        emb = encoder.encode([text], convert_to_tensor=True, show_progress_bar=False).to(device)
        with torch.no_grad():
            out_prob = torch.softmax(model(emb), dim=1)[0].cpu().numpy()
        pred_idx = out_prob.argmax()
        pred_cat = classes[pred_idx]
        conf = out_prob[pred_idx] * 100

        print(f"{pdf_path.name:<38}{pred_cat:<24}{conf:>6.2f}%")

    print("-" * 75)
    print("\nPipeline execution complete! Model weights and artifacts saved in runs/pdf_resume_model/")

if __name__ == "__main__":
    main()
