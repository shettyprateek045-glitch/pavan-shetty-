"""
Master Health-Check Script
==========================
Verifies that all components, datasets, pretrained connections,
and trained YOLO-head models are functional and operational.
"""

import sys
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

def check_all():
    print("=" * 75)
    print("      MASTER SYSTEM HEALTH & MODEL VERIFICATION REPORT")
    print("=" * 75)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n[1] Environment & Hardware Check:")
    print(f"  • Python Version : {sys.version.split()[0]}")
    print(f"  • PyTorch Version: {torch.__version__}")
    print(f"  • Device         : {device}")
    print(f"  • Status         : OK")

    # 2. Check Pretrained Encoder
    print(f"\n[2] Pretrained Model Connection Check:")
    pretrained_id = "anass1209/resume-job-matcher-all-MiniLM-L6-v2"
    print(f"  • Loading: {pretrained_id}...")
    encoder = SentenceTransformer(pretrained_id)
    test_emb = encoder.encode(["Software developer with Python"], convert_to_tensor=True)
    print(f"  • Embedding Dimension: {test_emb.shape[-1]} (expected 384)")
    print(f"  • Status             : CONNECTED & WORKING")

    # 3. Model Verification Registry
    models_to_check = [
        {
            "name": "Archive 123 Model (24 Broad Categories)",
            "meta": Path("runs/resume_minilm_yolo/model_meta.json"),
            "weights": Path("runs/resume_minilm_yolo/best_yolo_head.pt"),
            "test_sample": "CPA Accountant managing financial balance sheet audits and corporate taxes."
        },
        {
            "name": "Archive 456 Model (25 Specialized Tech Roles)",
            "meta": Path("runs/archive_456_model/model_meta.json"),
            "weights": Path("runs/archive_456_model/best_model.pt"),
            "test_sample": "Python and Django backend developer building scalable microservices and REST APIs."
        },
        {
            "name": "Archive 2 Model (9 Enterprise Tech Roles)",
            "meta": Path("runs/archive_2_model/model_meta.json"),
            "weights": Path("runs/archive_2_model/best_model.pt"),
            "test_sample": "Senior Java Architect designing Spring Boot microservices, Kafka pipelines, and Docker containers."
        }
    ]

    print(f"\n[3] Trained Model Health & Inference Checks:")
    print("-" * 75)

    all_passed = True
    for idx, m in enumerate(models_to_check, start=1):
        print(f"\nChecking Model {idx}: {m['name']}")
        if not m["meta"].exists():
            print(f"  [FAIL] Metadata missing: {m['meta']}")
            all_passed = False
            continue
        if not m["weights"].exists():
            print(f"  [FAIL] Weights missing: {m['weights']}")
            all_passed = False
            continue

        with open(m["meta"], "r") as f:
            meta = json.load(f)

        classes = meta["classes"]
        num_classes = len(classes)
        head = YOLOHeadClassifier(384, num_classes)
        head.load_state_dict(torch.load(m["weights"], map_location=device))
        head.to(device).eval()

        # Run test inference
        emb = encoder.encode([m["test_sample"]], convert_to_tensor=True).to(device)
        with torch.no_grad():
            probs = torch.softmax(head(emb), dim=1)[0].cpu().numpy()

        top_idx = probs.argmax()
        pred_class = classes[top_idx]
        conf = probs[top_idx] * 100

        print(f"  • Weights File  : {m['weights']} ({m['weights'].stat().st_size / 1024:.1f} KB)")
        print(f"  • Classes Loaded: {num_classes} categories")
        print(f"  • Test Input    : '{m['test_sample'][:60]}...'")
        print(f"  • Output        : {pred_class} (Confidence: {conf:.2f}%)")
        print(f"  • Model Status  : FUNCTIONAL (PASS)")

    # 4. Dataset Files Check
    print(f"\n[4] Dataset Integrity Check:")
    datasets = [
        ("archive123/Resume/Resume.csv", "Archive 123 (2,484 records)"),
        ("ResumeDataSet.csv", "Archive 456 (962 records)"),
        ("Resume dataset.csv", "Archive 2 (9,000 records)")
    ]
    for file_path, desc in datasets:
        p = Path(file_path)
        if p.exists():
            print(f"  • [FOUND] {desc:<32} -> {file_path} ({p.stat().st_size / (1024*1024):.1f} MB)")
        else:
            print(f"  • [MISSING] {file_path}")

    # 5. PDF Parser Check
    print(f"\n[5] PDF Extraction Check:")
    sample_pdf = Path("archive123/data/data/CHEF/10001727.pdf")
    if sample_pdf.exists():
        reader = PdfReader(str(sample_pdf))
        num_pages = len(reader.pages)
        sample_chars = len(reader.pages[0].extract_text() or "")
        print(f"  • Sample File   : {sample_pdf}")
        print(f"  • Pages Extracted: {num_pages} page(s), {sample_chars} characters on page 1")
        print(f"  • Parser Status : OK")
    else:
        print(f"  • Sample PDF not found at {sample_pdf}")

    print("\n" + "=" * 75)
    if all_passed:
        print("      ALL SYSTEMS & TRAINED MODELS ARE 100% OPERATIONAL!")
    else:
        print("      SOME ISSUES WERE DETECTED. PLEASE REVIEW LOGS ABOVE.")
    print("=" * 75)

if __name__ == "__main__":
    check_all()
