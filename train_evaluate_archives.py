"""
Train, Test, and Evaluate on Archive 456 and Archive 2
Using MiniLM-L6-v2 + YOLO-Head Architecture
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
from sklearn.metrics import classification_report, accuracy_score

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sentence_transformers import SentenceTransformer

SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)

PRETRAINED_ID = "anass1209/resume-job-matcher-all-MiniLM-L6-v2"
EMBED_DIM = 384

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

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def train_and_eval(name, df, text_col, label_col, output_dir, encoder, epochs=30, sample_per_class=None):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("\n" + "=" * 70)
    print(f"   TRAINING & EVALUATION PIPELINE: {name}")
    print("=" * 70)

    # Balance/sample if needed
    if sample_per_class:
        dfs = [group.sample(min(len(group), sample_per_class), random_state=SEED) for _, group in df.groupby(label_col)]
        df = pd.concat(dfs, ignore_index=True)

    df["clean_text"] = df[text_col].apply(clean_text)
    label_enc = LabelEncoder()
    df["label"] = label_enc.fit_transform(df[label_col])
    classes = list(label_enc.classes_)
    num_classes = len(classes)

    print(f"Dataset Size: {len(df)} samples across {num_classes} classes.")
    print(f"Classes: {classes[:4]} ... {classes[-3:]}")

    # Embeddings cache
    cache_path = output_dir / "embeddings.npy"
    if cache_path.exists():
        print(f"Loading cached embeddings from {cache_path}...")
        embeddings = np.load(str(cache_path))
    else:
        print(f"Encoding {len(df)} texts using {PRETRAINED_ID} (batch_size=128)...")
        t0 = time.time()
        embeddings = encoder.encode(
            df["clean_text"].tolist(),
            batch_size=128,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        np.save(str(cache_path), embeddings)
        print(f"Encoding completed in {time.time()-t0:.1f}s. Shape: {embeddings.shape}")

    # Split
    labels = df["label"].values
    X_tr, X_val, y_tr, y_val = train_test_split(
        embeddings, labels, test_size=0.2, random_state=SEED, stratify=labels
    )
    print(f"Train samples: {len(y_tr)}, Validation samples: {len(y_val)}")

    train_loader = DataLoader(EmbeddingDataset(X_tr, y_tr), batch_size=32, shuffle=True, drop_last=True)
    val_loader = DataLoader(EmbeddingDataset(X_val, y_val), batch_size=64, shuffle=False)

    # Model
    model = YOLOHeadClassifier(EMBED_DIM, num_classes).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.05)

    print(f"\nTraining YOLO-Head on {name} for {epochs} epochs...")
    best_val_acc = 0.0

    for epoch in range(1, epochs + 1):
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
        tr_acc = (correct / total) * 100

        # Validate
        model.eval()
        v_correct, v_total = 0, 0
        with torch.no_grad():
            for Xb, yb in val_loader:
                Xb, yb = Xb.to(device), yb.to(device)
                out = model(Xb)
                v_correct += (out.argmax(1) == yb).sum().item()
                v_total += len(yb)
        val_acc = (v_correct / v_total) * 100

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), output_dir / "best_model.pt")

        if epoch in [1, 5, 10, 20, 30] or val_acc == best_val_acc:
            best_tag = " *" if val_acc == best_val_acc else ""
            print(f"  Epoch {epoch:2d}/{epochs} | Train Acc: {tr_acc:6.2f}% | Val Acc: {val_acc:6.2f}%{best_tag}")

    # Save meta
    meta = {
        "dataset_name": name,
        "classes": classes,
        "num_classes": num_classes,
        "embed_dim": EMBED_DIM,
        "best_val_acc": round(best_val_acc, 2),
        "total_samples": len(df)
    }
    with open(output_dir / "model_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    # Final Evaluation on Best Model
    print(f"\n--- Evaluation Report for {name} (Best Val Acc: {best_val_acc:.2f}%) ---")
    model.load_state_dict(torch.load(output_dir / "best_model.pt"))
    model.eval()

    val_tensor = torch.tensor(X_val, dtype=torch.float32).to(device)
    with torch.no_grad():
        val_logits = model(val_tensor)
        val_probs = torch.softmax(val_logits, dim=1).cpu().numpy()

    preds = val_probs.argmax(axis=1)

    top3_correct = sum(1 for i, t in enumerate(y_val) if t in val_probs[i].argsort()[-3:])
    top3_acc = (top3_correct / len(y_val)) * 100

    print(f"Top-1 Accuracy: {accuracy_score(y_val, preds)*100:.2f}%")
    print(f"Top-3 Accuracy: {top3_acc:.2f}%")
    report = classification_report(y_val, preds, target_names=classes, digits=4, zero_division=0)
    print(report)

    with open(output_dir / "classification_report.txt", "w") as f:
        f.write(report)

    return model, classes, best_val_acc

def main():
    print("=" * 70)
    print("   CONNECTING PRETRAINED MODEL (MiniLM) TO YOLO-HEAD")
    print("   TRAINING & EVALUATION ON ARCHIVE 456 & ARCHIVE 2")
    print("=" * 70)

    print("\nLoading Pretrained Transformer:", PRETRAINED_ID)
    encoder = SentenceTransformer(PRETRAINED_ID)
    print("Encoder ready.")

    # 1. Archive 456 (ResumeDataSet.csv)
    df_456 = pd.read_csv("ResumeDataSet.csv")
    model_456, classes_456, acc_456 = train_and_eval(
        name="Archive 456 (ResumeDataSet)",
        df=df_456,
        text_col="Resume",
        label_col="Category",
        output_dir="runs/archive_456_model",
        encoder=encoder,
        epochs=30
    )

    # 2. Archive 2 (Resume dataset.csv)
    df_2 = pd.read_csv("Resume dataset.csv")
    model_2, classes_2, acc_2 = train_and_eval(
        name="Archive 2 (Enterprise Resumes)",
        df=df_2,
        text_col="Text",
        label_col="category",
        output_dir="runs/archive_2_model",
        encoder=encoder,
        epochs=30,
        sample_per_class=350  # 3,150 balanced enterprise samples for speed & high accuracy
    )

    # 3. Live text testing on both models
    print("\n" + "=" * 70)
    print("   LIVE INFERENCE TESTING ON BOTH TRAINED MODELS")
    print("=" * 70)

    test_samples = [
        "Experienced Python Developer with expertise in Django, Flask, PyTorch, REST APIs, and PostgreSQL database design.",
        "Senior Java Architect designing microservices using Spring Boot, Kafka, Docker, Kubernetes, and Hibernate.",
        "Senior SQL Developer with 8 years writing complex stored procedures, database indexing, ETL pipelines, and performance tuning.",
        "HR Recruiter with full lifecycle recruitment, candidate screening, sourcing on LinkedIn, and technical onboarding."
    ]

    print("\n--- Testing Archive 456 Model (25 Specialized Roles) ---")
    model_456.eval()
    for s in test_samples:
        clean = clean_text(s)
        emb = encoder.encode([clean], convert_to_tensor=True, show_progress_bar=False)
        with torch.no_grad():
            probs = torch.softmax(model_456(emb), dim=1)[0].cpu().numpy()
        top_idx = probs.argmax()
        print(f"Sample: '{s[:65]}...'")
        print(f" -> Predicted: {classes_456[top_idx]} ({probs[top_idx]*100:.2f}%)\n")

    print("\n--- Testing Archive 2 Model (9 Enterprise Tech Roles) ---")
    model_2.eval()
    for s in test_samples:
        clean = clean_text(s)
        emb = encoder.encode([clean], convert_to_tensor=True, show_progress_bar=False)
        with torch.no_grad():
            probs = torch.softmax(model_2(emb), dim=1)[0].cpu().numpy()
        top_idx = probs.argmax()
        print(f"Sample: '{s[:65]}...'")
        print(f" -> Predicted: {classes_2[top_idx]} ({probs[top_idx]*100:.2f}%)\n")

    print("=" * 70)
    print(f"SUMMARY: Archive 456 Val Acc = {acc_456:.2f}% | Archive 2 Val Acc = {acc_2:.2f}%")
    print("ALL MODELS TRAINED, TESTED, AND EVALUATED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()
