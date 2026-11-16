"""
Interactive Testing Script for Resume Classifier (MiniLM + YOLO-Head)
=====================================================================
Tests:
1. Real PDF resumes from disk across 8 diverse categories.
2. User's personal resume file: Prateek_Shetty_Resume.pdf.
3. Natural language job / profile descriptions.
"""

import sys
import time
import json
from pathlib import Path

import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

# Architecture definition
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

def clean_text(text: str) -> str:
    import re
    if not isinstance(text, str):
        return ""
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    return " ".join([page.extract_text() or "" for page in reader.pages])

def main():
    print("=" * 80)
    print("       LIVE COMPREHENSIVE MODEL INFERENCE & TESTING SUITE")
    print("=" * 80)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Load Encoder
    model_id = "anass1209/resume-job-matcher-all-MiniLM-L6-v2"
    print(f"Loading Pretrained Encoder: {model_id}...")
    encoder = SentenceTransformer(model_id)

    # Load PDF Model (24 classes)
    meta_path = Path("runs/pdf_resume_model/model_meta.json")
    weights_path = Path("runs/pdf_resume_model/best_model.pt")
    with open(meta_path) as f:
        meta = json.load(f)
    classes = meta["classes"]
    num_classes = len(classes)

    model = YOLOHeadClassifier(384, num_classes)
    model.load_state_dict(torch.load(weights_path, map_location=device))
    model.to(device).eval()
    print(f"Loaded YOLO-Head ({num_classes} classes) from {weights_path}")

    # Load Archive 456 Model (25 classes, tech specialized)
    meta_456_path = Path("runs/archive_456_model/model_meta.json")
    weights_456_path = Path("runs/archive_456_model/best_model.pt")
    with open(meta_456_path) as f:
        meta_456 = json.load(f)
    classes_456 = meta_456["classes"]
    model_456 = YOLOHeadClassifier(384, len(classes_456))
    model_456.load_state_dict(torch.load(weights_456_path, map_location=device))
    model_456.to(device).eval()

    def predict(text, top_k=3, use_456=False):
        c_list = classes_456 if use_456 else classes
        m = model_456 if use_456 else model

        cleaned = clean_text(text)
        t0 = time.time()
        with torch.no_grad():
            emb = encoder.encode([cleaned], convert_to_tensor=True).to(device)
            probs = torch.softmax(m(emb), dim=1)[0].cpu().numpy()
        latency = (time.time() - t0) * 1000

        top_indices = probs.argsort()[-top_k:][::-1]
        preds = [(c_list[i], float(probs[i])) for i in top_indices]
        return preds, latency

    # -------------------------------------------------------------
    # TEST SUITE 1: Actual PDF Files from disk across various domains
    # -------------------------------------------------------------
    print("\n" + "-" * 80)
    print("TEST SUITE 1: REAL PDF RESUMES FROM DISK (archive123)")
    print("-" * 80)

    pdf_tests = [
        ("archive123/data/data/CHEF/10001727.pdf", "CHEF"),
        ("archive123/data/data/ACCOUNTANT/10554236.pdf", "ACCOUNTANT"),
        ("archive123/data/data/INFORMATION-TECHNOLOGY/10089434.pdf", "INFORMATION-TECHNOLOGY"),
        ("archive123/data/data/AVIATION/11759079.pdf", "AVIATION"),
        ("archive123/data/data/TEACHER/10144983.pdf", "TEACHER"),
        ("archive123/data/data/CONSTRUCTION/10255397.pdf", "CONSTRUCTION"),
        ("archive123/data/data/FITNESS/10058474.pdf", "FITNESS"),
        ("archive123/data/data/HR/10674770.pdf", "HR"),
    ]

    print(f"{'PDF File Name':<28}{'Expected':<18}{'Top-1 Prediction':<24}{'Confidence':<12}{'Match'}")
    print("-" * 80)

    for pdf_str, expected in pdf_tests:
        p = Path(pdf_str)
        if not p.exists():
            continue
        text = extract_pdf_text(p)
        preds, lat = predict(text)
        top1, conf = preds[0]
        matched = "PASS" if top1 == expected else "FAIL"
        print(f"{p.name:<28}{expected:<18}{top1:<24}{conf*100:>6.2f}%      {matched}")

    # -------------------------------------------------------------
    # TEST SUITE 2: User's Personal Resume (Prateek_Shetty_Resume.pdf)
    # -------------------------------------------------------------
    print("\n" + "-" * 80)
    print("TEST SUITE 2: USER'S PERSONAL RESUME (Prateek_Shetty_Resume.pdf)")
    print("-" * 80)

    user_resume = Path("Prateek_Shetty_Resume.pdf")
    if user_resume.exists():
        text = extract_pdf_text(user_resume)
        print(f"File Name: {user_resume.name} (Extracted {len(text)} characters)")

        # Evaluate on Archive 456 Tech Model
        preds_456, lat = predict(text, top_k=3, use_456=True)
        print("\nPredictions by Specialized Tech Model (Archive 456):")
        for rank, (cat, conf) in enumerate(preds_456, 1):
            print(f"  #{rank}: {cat:<25} ({conf*100:.2f}%)")

        # Evaluate on General PDF Model (Archive 123)
        preds_123, _ = predict(text, top_k=3, use_456=False)
        print("\nPredictions by Broad Industry Model (Archive 123):")
        for rank, (cat, conf) in enumerate(preds_123, 1):
            print(f"  #{rank}: {cat:<25} ({conf*100:.2f}%)")

    # -------------------------------------------------------------
    # TEST SUITE 3: Free-Text Natural Language Job & Profile Queries
    # -------------------------------------------------------------
    print("\n" + "-" * 80)
    print("TEST SUITE 3: NATURAL LANGUAGE CANDIDATE DESCRIPTIONS")
    print("-" * 80)

    text_queries = [
        "Specialized in deep learning, neural networks, PyTorch, computer vision, OpenCV, and edge AI deployment on NVIDIA Jetson.",
        "Experienced corporate lawyer with bar admission, contract dispute resolution, trademark protection, and legal compliance.",
        "Pastry and sous chef with expertise in banquet preparation, food safety standards, kitchen brigade operations, and fine dining.",
        "Certified flight instructor and commercial airline pilot with multi-engine rating, flight logs, and glass cockpit navigation."
    ]

    for q in text_queries:
        preds, lat = predict(q, top_k=2)
        print(f"\nQuery: \"{q[:75]}...\"")
        print(f"  • Top Prediction: {preds[0][0]} ({preds[0][1]*100:.2f}%)")
        print(f"  • Runner-Up     : {preds[1][0]} ({preds[1][1]*100:.2f}%)")
        print(f"  • Latency       : {lat:.1f} ms")

    print("\n" + "=" * 80)
    print("       ALL TEST SUITES COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    main()
