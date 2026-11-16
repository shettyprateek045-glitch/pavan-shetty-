"""
Resume Intelligence Service
===========================
Connects all trained models and provides ATS Resume Checking, Scoring,
and Semantic Matching features modeled after professional ATS checkers (e.g. Zety).

Models Connected:
1. Pretrained Semantic Encoder: anass1209/resume-job-matcher-all-MiniLM-L6-v2 (384-dim)
2. Archive 123 PDF Model (24 Broad Industry Categories)
3. Archive 456 Model (25 Specialized Tech Roles)
4. Archive 2 Model (9 Enterprise Tech Roles)
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import torch
import torch.nn as nn
from pypdf import PdfReader

logger = logging.getLogger("resume-service")
logging.basicConfig(level=logging.INFO)

# Single-Shot YOLOv11 Head Architecture
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


class ResumeIntelligenceService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.encoder = None
        self.encoder_loaded = False
        
        # Models registry
        self.models: Dict[str, Dict[str, Any]] = {}
        
        # Initialize
        self._load_encoder()
        self._load_all_models()

    def _load_encoder(self):
        model_id = "anass1209/resume-job-matcher-all-MiniLM-L6-v2"
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading Pretrained Sentence Transformer: {model_id}")
            self.encoder = SentenceTransformer(model_id)
            self.encoder_loaded = True
            logger.info("Semantic Sentence Transformer loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer: {e}. Semantic features will use fallback vectorizer.")
            self.encoder = None
            self.encoder_loaded = False

    def _load_all_models(self):
        """Loads Archive 123, Archive 456, and Archive 2 models."""
        configs = [
            ("archive_123_pdf", Path("runs/pdf_resume_model")),
            ("archive_456_tech", Path("runs/archive_456_model")),
            ("archive_2_enterprise", Path("runs/archive_2_model")),
            ("archive_123_legacy", Path("runs/resume_minilm_yolo"))
        ]

        for key, dir_path in configs:
            meta_path = dir_path / "model_meta.json"
            weights_path = dir_path / "best_model.pt"
            if not weights_path.exists():
                weights_path = dir_path / "best_yolo_head.pt"

            if meta_path.exists() and weights_path.exists():
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    classes = meta["classes"]
                    head = YOLOHeadClassifier(384, len(classes))
                    head.load_state_dict(torch.load(weights_path, map_location=self.device))
                    head.to(self.device).eval()
                    self.models[key] = {
                        "model": head,
                        "classes": classes,
                        "num_classes": len(classes),
                        "weights": str(weights_path),
                        "meta": meta
                    }
                    logger.info(f"Loaded {key} with {len(classes)} classes from {weights_path}")
                except Exception as e:
                    logger.warning(f"Failed loading {key}: {e}")

    def clean_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = re.sub(r"http\S+", " ", text)
        text = re.sub(r"[^\w\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def extract_text_from_pdf(self, pdf_file) -> str:
        try:
            reader = PdfReader(pdf_file)
            return " ".join([page.extract_text() or "" for page in reader.pages])
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            return ""

    def get_embedding(self, text: str):
        """Generates or returns tensor embedding using the shared SentenceTransformer."""
        cleaned = self.clean_text(text)
        if not cleaned or not self.encoder_loaded or self.encoder is None:
            return None
        with torch.no_grad():
            return self.encoder.encode([cleaned], convert_to_tensor=True).to(self.device)

    def classify_with_embedding(self, emb) -> Dict[str, Any]:
        """Runs fast single-shot inference on precomputed tensor embedding."""
        results = {}
        if emb is None:
            return results
        with torch.no_grad():
            for key, item in self.models.items():
                m = item["model"]
                c_list = item["classes"]
                probs = torch.softmax(m(emb), dim=1)[0].cpu().numpy()
                top3_idx = probs.argsort()[-3:][::-1]
                results[key] = [
                    {"category": c_list[i], "confidence": round(float(probs[i]) * 100, 2)}
                    for i in top3_idx
                ]
        return results

    def classify_all_models(self, text: str) -> Dict[str, Any]:
        """Runs single-shot inference on all connected models."""
        cleaned = self.clean_text(text)
        if not cleaned:
            return {"error": "Empty text after cleaning"}

        if not self.encoder_loaded or self.encoder is None:
            return {"error": "Sentence Transformer encoder not loaded"}

        emb = self.get_embedding(cleaned)
        return self.classify_with_embedding(emb)

    def analyze_ats_resume(self, text: str, job_description: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive ATS & Resume Health Assessment (Zety-Style Feature Suite):
        1. ATS Readability & Overall Score (0-100)
        2. Essential Sections Detection (Experience, Education, Skills, Contact, Summary, Projects)
        3. Measurable Metrics & Action Verbs Analysis
        4. Word Count, Reading Time & Formatting Checks
        5. Keyword / Job Match Score (via Cosine Similarity)
        6. Actionable Recommendations & Improvement Tips
        7. AI Category Classification from all connected models
        """
        text_lower = text.lower()
        word_list = re.findall(r"\b\w+\b", text)
        word_count = len(word_list)

        # 1. Section Presence Evaluation
        sections = {
            "Contact Information": bool(re.search(r"(@|\bphone\b|\bemail\b|\blinkedin\b|\bgithub\b|\bmobile\b)", text_lower)),
            "Professional Summary": bool(re.search(r"\b(summary|profile|about me|objective|overview)\b", text_lower)),
            "Work Experience": bool(re.search(r"\b(experience|employment|work history|career|professional background)\b", text_lower)),
            "Education": bool(re.search(r"\b(education|university|college|bachelor|master|b\.e|b\.tech|degree|diploma)\b", text_lower)),
            "Skills": bool(re.search(r"\b(skills|technologies|proficiencies|competencies|tools)\b", text_lower)),
            "Projects": bool(re.search(r"\b(projects|portfolio|open source|key initiatives)\b", text_lower)),
            "Certifications / Awards": bool(re.search(r"\b(certif|credentials|award|honors|licensed)\b", text_lower))
        }

        # 2. Measurable Metrics & Action Verbs Check
        action_verbs = [
            "developed", "designed", "implemented", "engineered", "built", "spearheaded",
            "managed", "led", "architected", "optimized", "increased", "reduced",
            "delivered", "orchestrated", "automated", "created", "deployed", "scaled"
        ]
        found_verbs = [verb for verb in action_verbs if re.search(rf"\b{verb}\b", text_lower)]
        metric_matches = re.findall(r"(\b\d+%\b|\$\d+|\b\d+\+\b|\b\d+\s*(?:users|clients|ms|seconds|hours|team members|developers|projects|million|k)\b)", text_lower)

        # 3. Contact Info extraction
        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        phones = re.findall(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
        linkedin = "linkedin.com" in text_lower or "linkedin" in text_lower
        github = "github.com" in text_lower or "github" in text_lower

        # 4. ATS Scoring Algorithm
        score = 0
        feedback = []

        # Sections (Max 35 points)
        sec_count = sum(sections.values())
        score += int((sec_count / len(sections)) * 35)
        for sec, present in sections.items():
            if not present:
                feedback.append({
                    "type": "warning",
                    "category": "Sections",
                    "title": f"Missing {sec}",
                    "detail": f"Adding a clearly labeled '{sec}' section improves ATS scan efficiency and recruiter navigation."
                })

        # Measurable Impact & Verbs (Max 25 points)
        verb_score = min(len(found_verbs) * 3, 15)
        metric_score = min(len(metric_matches) * 2, 10)
        score += (verb_score + metric_score)

        if len(metric_matches) < 3:
            feedback.append({
                "type": "improvement",
                "category": "Impact",
                "title": "Add Measurable Metrics",
                "detail": "Quantify your achievements with numbers, percentages, or cost savings (e.g., 'Optimized query latency by 45%')."
            })

        if len(found_verbs) < 4:
            feedback.append({
                "type": "improvement",
                "category": "Action Verbs",
                "title": "Use Stronger Action Verbs",
                "detail": "Start bullet points with strong verbs (e.g., 'Architected', 'Spearheaded') rather than 'Responsible for'."
            })

        # Length & Formatting (Max 20 points)
        if 250 <= word_count <= 900:
            score += 20
        elif word_count < 250:
            score += 8
            feedback.append({
                "type": "warning",
                "category": "Length",
                "title": "Resume Too Brief",
                "detail": f"Word count is {word_count}. Standard professional resumes contain between 350-800 words."
            })
        else:
            score += 12
            feedback.append({
                "type": "suggestion",
                "category": "Length",
                "title": "Resume is Rather Long",
                "detail": f"Word count is {word_count}. Ensure experience is crisp and relevant to stay within 1-2 pages."
            })

        # Contact Details (Max 20 points)
        contact_score = 0
        if emails: contact_score += 8
        if phones: contact_score += 6
        if linkedin or github: contact_score += 6
        score += contact_score

        if not emails:
            feedback.append({"type": "critical", "category": "Contact", "title": "Missing Email Address", "detail": "Add a professional email address at the top."})
        if not phones:
            feedback.append({"type": "warning", "category": "Contact", "title": "Missing Phone Number", "detail": "Include a standard international phone format."})

        # Clamp score 0 - 100
        overall_score = max(min(score, 100), 10)

        # 5. Semantic Job Match (if Job Description is provided)
        job_match = None
        if job_description and self.encoder_loaded and self.encoder is not None:
            clean_jd = self.clean_text(job_description)
            clean_res = self.clean_text(text)
            with torch.no_grad():
                res_emb = self.encoder.encode([clean_res], convert_to_tensor=True)
                jd_emb = self.encoder.encode([clean_jd], convert_to_tensor=True)
                cos_sim = torch.cosine_similarity(res_emb, jd_emb).item()
                match_percentage = round(max(min(cos_sim * 100, 100), 0), 2)

            # Keyword overlap analysis
            jd_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", clean_jd.lower()))
            res_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", clean_res.lower()))
            common_kw = list(jd_words.intersection(res_words))
            missing_kw = list(jd_words.difference(res_words))

            job_match = {
                "similarity_score": match_percentage,
                "common_keywords": common_kw[:12],
                "missing_keywords": missing_kw[:10],
                "fit_level": "Excellent Match" if match_percentage >= 75 else ("Good Match" if match_percentage >= 50 else "Low Match")
            }

        # 6. Model Classifications
        classifications = self.classify_all_models(text)

        return {
            "overall_ats_score": overall_score,
            "status_label": "Excellent" if overall_score >= 80 else ("Good" if overall_score >= 65 else "Needs Improvement"),
            "word_count": word_count,
            "estimated_read_time_seconds": round(word_count / 3.5),
            "contact_details": {
                "emails": emails[:2],
                "phones": phones[:2],
                "linkedin": linkedin,
                "github": github
            },
            "sections_audit": sections,
            "action_verbs_found": found_verbs,
            "metrics_detected": metric_matches[:6],
            "feedback": feedback,
            "job_match": job_match,
            "model_predictions": classifications
        }


# Singleton instance
resume_engine = ResumeIntelligenceService()
