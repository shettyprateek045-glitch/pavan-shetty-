"""
predict_minilm_yolo.py
======================
Single-shot resume inference using MiniLM + YOLO-Head.

Usage:
  python predict_minilm_yolo.py --input "resume text goes here"
  python predict_minilm_yolo.py --input path/to/resume.pdf
  python predict_minilm_yolo.py --input path/to/resumes_folder/
  python predict_minilm_yolo.py --batch path/to/Resume.csv --out results.csv
"""

import re
import sys
import json
import argparse
from pathlib import Path

import torch
import torch.nn as nn
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("ERROR: Run `pip install sentence-transformers` first.")
    sys.exit(1)

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


# ─────────────────────────────────────────────────────────────────────────────
# YOLO-Head (must match training definition)
# ─────────────────────────────────────────────────────────────────────────────
class YOLOHeadClassifier(nn.Module):
    def __init__(self, input_dim: int, num_classes: int, dropout: float = 0.3):
        super().__init__()
        self.head = nn.Sequential(
            nn.Linear(input_dim, 512), nn.BatchNorm1d(512), nn.SiLU(), nn.Dropout(dropout),
            nn.Linear(512, 256),       nn.BatchNorm1d(256), nn.SiLU(), nn.Dropout(dropout),
            nn.Linear(256, 128),       nn.BatchNorm1d(128), nn.SiLU(), nn.Dropout(0.1),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        return self.head(x)


# ─────────────────────────────────────────────────────────────────────────────
# Predictor — loads model once, reuses for multiple calls
# ─────────────────────────────────────────────────────────────────────────────
class ResumePredictor:
    def __init__(self, model_dir: str = "runs/resume_minilm_yolo"):
        model_dir = Path(model_dir)
        meta_path = model_dir / "model_meta.json"
        if not meta_path.exists():
            raise FileNotFoundError(
                f"model_meta.json not found in {model_dir}. "
                "Run train_minilm_yolo_classifier.py first."
            )

        with open(meta_path) as f:
            self.meta = json.load(f)

        self.classes     = self.meta["classes"]
        self.num_classes = self.meta["num_classes"]
        self.embed_dim   = self.meta["embed_dim"]
        self.device      = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        print(f"[Predictor] Loading encoder: {self.meta['encoder_id']} …")
        self.encoder = SentenceTransformer(self.meta["encoder_id"])

        print("[Predictor] Loading YOLO-Head weights …")
        self.yolo_head = YOLOHeadClassifier(self.embed_dim, self.num_classes)
        self.yolo_head.load_state_dict(
            torch.load(model_dir / "best_yolo_head.pt", map_location=self.device)
        )
        self.yolo_head.to(self.device).eval()
        print("[Predictor] Ready.\n")

    # ── helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _clean(text: str) -> str:
        text = re.sub(r"http\S+", " ", text or "")
        text = re.sub(r"[^\w\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _read_pdf(path) -> str:
        if PdfReader is None:
            raise ImportError("pypdf not installed. Run: pip install pypdf")
        reader = PdfReader(str(path))
        return " ".join(page.extract_text() or "" for page in reader.pages)

    # ── core inference ────────────────────────────────────────────────────────
    def predict_texts(self, texts: list[str], top_k: int = 3) -> list[dict]:
        cleaned    = [self._clean(t) for t in texts]
        embeddings = self.encoder.encode(cleaned, convert_to_tensor=True,
                                         show_progress_bar=False)
        embeddings = embeddings.to(self.device)

        with torch.no_grad():
            probs = torch.softmax(self.yolo_head(embeddings), dim=1).cpu().numpy()

        results = []
        for prob_row in probs:
            top_idx = prob_row.argsort()[-top_k:][::-1]
            results.append({
                "top1"       : self.classes[top_idx[0]],
                "top1_conf"  : float(prob_row[top_idx[0]]),
                "predictions": [
                    {"category": self.classes[i], "confidence": float(prob_row[i])}
                    for i in top_idx
                ],
            })
        return results

    def predict_pdf(self, pdf_path, top_k: int = 3) -> dict:
        text = self._read_pdf(pdf_path)
        return self.predict_texts([text], top_k=top_k)[0]

    def predict_folder(self, folder: Path, top_k: int = 3) -> list[dict]:
        pdfs = list(folder.glob("**/*.pdf"))
        if not pdfs:
            print(f"No PDF files found in {folder}")
            return []
        texts = [self._read_pdf(p) for p in pdfs]
        preds = self.predict_texts(texts, top_k=top_k)
        for i, p in enumerate(preds):
            p["file"] = str(pdfs[i])
        return preds

    # ── pretty print ─────────────────────────────────────────────────────────
    @staticmethod
    def display(result: dict, header: str = ""):
        if header:
            print(f"\n{'─'*50}\n  {header}\n{'─'*50}")
        print(f"  ▶  {result['top1']}  ({result['top1_conf']*100:.2f}%)")
        for p in result["predictions"][1:]:
            print(f"     {p['category']:<30} {p['confidence']*100:.2f}%")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="MiniLM + YOLO-Head Resume Predictor")
    ap.add_argument("--input",    type=str, help="Text, PDF path, or folder path")
    ap.add_argument("--batch",    type=str, help="CSV file with Resume_str column")
    ap.add_argument("--out",      type=str, default="predictions.csv",
                    help="Output CSV for --batch mode (default: predictions.csv)")
    ap.add_argument("--top_k",   type=int, default=3,
                    help="Number of top categories to show (default: 3)")
    ap.add_argument("--model_dir", type=str, default="runs/resume_minilm_yolo")
    args = ap.parse_args()

    predictor = ResumePredictor(model_dir=args.model_dir)

    # ── Batch CSV mode ────────────────────────────────────────────────────────
    if args.batch:
        import pandas as pd
        df    = pd.read_csv(args.batch)
        texts = df["Resume_str"].fillna("").tolist()
        print(f"Predicting {len(texts)} resumes …")
        preds = predictor.predict_texts(texts, top_k=1)
        df["predicted_category"] = [p["top1"]      for p in preds]
        df["confidence"]         = [p["top1_conf"] for p in preds]
        df.to_csv(args.out, index=False)
        print(f"Saved to {args.out}")
        if "Category" in df.columns:
            acc = (df["predicted_category"] == df["Category"]).mean() * 100
            print(f"Accuracy on this CSV: {acc:.2f}%")
        return

    # ── Single / folder mode ──────────────────────────────────────────────────
    if not args.input:
        # demo
        samples = [
            "Senior Python developer with 7 years experience in Django, REST APIs, PostgreSQL, Docker, AWS, and Kubernetes.",
            "Registered Nurse with ICU experience, patient triage, medication administration, and electronic health records.",
            "CPA with 10 years in financial reporting, tax compliance, GAAP, and corporate auditing.",
        ]
        print("Demo predictions:\n")
        preds = predictor.predict_texts(samples, top_k=args.top_k)
        for s, r in zip(samples, preds):
            predictor.display(r, header=s[:60] + "…")
        return

    target = Path(args.input)
    if target.is_dir():
        results = predictor.predict_folder(target, top_k=args.top_k)
        for r in results:
            predictor.display(r, header=r.get("file", ""))
    elif target.suffix.lower() == ".pdf":
        result = predictor.predict_pdf(target, top_k=args.top_k)
        predictor.display(result, header=str(target))
    else:
        result = predictor.predict_texts([args.input], top_k=args.top_k)[0]
        predictor.display(result, header="Input text")


if __name__ == "__main__":
    main()
