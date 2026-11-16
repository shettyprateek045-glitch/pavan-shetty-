import re
import json
import joblib
from pathlib import Path
import torch
import torch.nn as nn
from pypdf import PdfReader

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

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'http\S+\s*', ' ', text)
    text = re.sub(r'#\S+', '', text)
    text = re.sub(r'@\S+', '  ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()

class ResumePredictor:
    def __init__(self, model_dir="runs/resume_classifier"):
        model_dir = Path(model_dir)
        self.vectorizer = joblib.load(model_dir / "vectorizer.joblib")
        with open(model_dir / "classes.json", "r") as f:
            self.classes = json.load(f)

        input_dim = len(self.vectorizer.get_feature_names_out())
        num_classes = len(self.classes)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = ResumeClassifier(input_dim, num_classes)
        self.model.load_state_dict(torch.load(model_dir / "best_model.pt", map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

    def predict_text(self, text, top_k=3):
        cleaned = clean_text(text)
        features = self.vectorizer.transform([cleaned]).toarray()
        tensor = torch.tensor(features, dtype=torch.float32).to(self.device)

        with torch.no_grad():
            logits = self.model(tensor)
            probs = torch.softmax(logits, dim=1)[0].cpu().numpy()

        top_indices = probs.argsort()[-top_k:][::-1]
        results = [
            {"category": self.classes[idx], "confidence": float(probs[idx])}
            for idx in top_indices
        ]
        return results

    def predict_pdf(self, pdf_path, top_k=3):
        reader = PdfReader(pdf_path)
        extracted = " ".join([page.extract_text() or "" for page in reader.pages])
        return self.predict_text(extracted, top_k=top_k)

if __name__ == "__main__":
    import sys
    predictor = ResumePredictor()
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if target.endswith(".pdf"):
            preds = predictor.predict_pdf(target)
        else:
            preds = predictor.predict_text(target)
        print("Predictions:")
        for p in preds:
            print(f" - {p['category']}: {p['confidence'] * 100:.2f}%")
    else:
        sample = "Proficient in Python, Django, REST APIs, PostgreSQL, Docker, AWS, and Machine Learning."
        print(f"Testing on sample: '{sample}'")
        preds = predictor.predict_text(sample)
        for p in preds:
            print(f" - {p['category']}: {p['confidence'] * 100:.2f}%")
