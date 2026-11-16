import os
import re
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, f1_score

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# Set random seeds for reproducibility
SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'http\S+\s*', ' ', text)  # remove URLs
    text = re.sub(r'#\S+', '', text)          # remove hashtags
    text = re.sub(r'@\S+', '  ', text)        # remove mentions
    text = re.sub(r'[^\w\s]', ' ', text)      # remove punctuation
    text = re.sub(r'\s+', ' ', text).strip()  # remove extra whitespace
    return text.lower()

class ResumeDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class ResumeClassifier(nn.Module):
    def __init__(self, input_dim, num_classes):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        return self.network(x)

def main():
    print("=" * 60)
    print("Resume Classification Model Training (archive123)")
    print("=" * 60)

    csv_path = Path("archive123/Resume/Resume.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    print(f"Loading dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} samples across {df['Category'].nunique()} categories.")

    # Clean text
    print("Preprocessing resume texts...")
    df['cleaned_resume'] = df['Resume_str'].apply(clean_text)

    # Encode labels
    label_encoder = LabelEncoder()
    df['label'] = label_encoder.fit_transform(df['Category'])
    classes = list(label_encoder.classes_)
    num_classes = len(classes)
    print(f"Categories ({num_classes}): {classes[:5]} ... {classes[-3:]}")

    # Train / Val split (stratified)
    X_train_raw, X_val_raw, y_train, y_val = train_test_split(
        df['cleaned_resume'], df['label'].values,
        test_size=0.2, random_state=SEED, stratify=df['label'].values
    )
    print(f"Train samples: {len(X_train_raw)}, Validation samples: {len(X_val_raw)}")

    # Vectorize with TF-IDF (max 5000 features, unigram + bigram)
    print("Extracting TF-IDF features...")
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
    X_train = vectorizer.fit_transform(X_train_raw).toarray()
    X_val = vectorizer.transform(X_val_raw).toarray()

    input_dim = X_train.shape[1]
    print(f"Feature vector size: {input_dim}")

    # Data loaders
    train_dataset = ResumeDataset(X_train, y_train)
    val_dataset = ResumeDataset(X_val, y_val)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)

    # Model & Training setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    model = ResumeClassifier(input_dim=input_dim, num_classes=num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=30)

    output_dir = Path("runs/resume_classifier")
    output_dir.mkdir(parents=True, exist_ok=True)

    epochs = 30
    best_val_acc = 0.0
    history = []

    print("-" * 60)
    print(f"Starting training for {epochs} epochs...")
    print(f"{'Epoch':<8}{'Train Loss':<14}{'Train Acc (%)':<16}{'Val Loss':<14}{'Val Acc (%)':<14}")
    print("-" * 60)

    for epoch in range(1, epochs + 1):
        # Training loop
        model.train()
        total_train_loss = 0.0
        correct_train = 0
        total_train = 0

        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()

            total_train_loss += loss.item() * len(y_batch)
            _, predicted = torch.max(outputs, 1)
            correct_train += (predicted == y_batch).sum().item()
            total_train += len(y_batch)

        scheduler.step()
        train_loss = total_train_loss / total_train
        train_acc = (correct_train / total_train) * 100

        # Validation loop
        model.eval()
        total_val_loss = 0.0
        correct_val = 0
        total_val = 0
        all_preds = []
        all_targets = []

        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)

                total_val_loss += loss.item() * len(y_batch)
                _, predicted = torch.max(outputs, 1)
                correct_val += (predicted == y_batch).sum().item()
                total_val += len(y_batch)

                all_preds.extend(predicted.cpu().numpy())
                all_targets.extend(y_batch.cpu().numpy())

        val_loss = total_val_loss / total_val
        val_acc = (correct_val / total_val) * 100

        history.append({
            "epoch": epoch,
            "train_loss": train_loss,
            "train_acc": train_acc,
            "val_loss": val_loss,
            "val_acc": val_acc
        })

        is_best = val_acc > best_val_acc
        if is_best:
            best_val_acc = val_acc
            torch.save(model.state_dict(), output_dir / "best_model.pt")

        best_marker = " *" if is_best else ""
        print(f"{epoch:<8}{train_loss:<14.4f}{train_acc:<16.2f}{val_loss:<14.4f}{val_acc:<14.2f}{best_marker}")

    # Save final model, vectorizer, and classes
    torch.save(model.state_dict(), output_dir / "final_model.pt")
    joblib.dump(vectorizer, output_dir / "vectorizer.joblib")
    with open(output_dir / "classes.json", "w") as f:
        json.dump(classes, f, indent=2)

    # Save training history
    pd.DataFrame(history).to_csv(output_dir / "training_history.csv", index=False)

    print("-" * 60)
    print(f"Training Complete! Peak Validation Accuracy: {best_val_acc:.2f}%")
    print(f"Best model weights saved to: {output_dir / 'best_model.pt'}")
    print(f"Vectorizer saved to: {output_dir / 'vectorizer.joblib'}")
    print(f"Class names saved to: {output_dir / 'classes.json'}")

    # Final Evaluation Report using best model
    model.load_state_dict(torch.load(output_dir / "best_model.pt"))
    model.eval()
    with torch.no_grad():
        val_tensor = torch.tensor(X_val, dtype=torch.float32).to(device)
        preds = torch.argmax(model(val_tensor), dim=1).cpu().numpy()

    report = classification_report(y_val, preds, target_names=classes, digits=4)
    print("\nFinal Classification Report on Validation Set:")
    print(report)

    with open(output_dir / "classification_report.txt", "w") as f:
        f.write(report)

if __name__ == "__main__":
    main()
