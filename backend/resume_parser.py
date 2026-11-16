"""
AI Resume Parser & Screening Engine
===================================
Robust text extraction for PDF and DOCX documents, NER entity parsing (Name, Email, Phone, Skills, Experience, Education),
multi-vector semantic matching with MiniLM-L6-v2 and PyTorch connected classifiers,
and automated decision categorization (Selected, Maybe, Rejected) with explainability.
"""

import io
import re
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

# Common skill taxonomies
TECH_SKILLS_TAXONOMY = {
    # Languages
    "python", "go", "golang", "java", "c++", "c#", "javascript", "typescript", "ruby", "rust", "scala", "php", "swift", "kotlin", "r",
    # Frameworks & Libraries
    "react", "react.js", "next.js", "vue", "angular", "node.js", "express", "fastapi", "django", "flask", "spring", "spring boot", "tailwind css",
    # Cloud & DevOps
    "docker", "kubernetes", "k8s", "aws", "gcp", "azure", "terraform", "ci/cd", "jenkins", "github actions", "ansible", "linux", "bash",
    # Data & Storage
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch", "kafka", "rabbitmq", "cassandra", "dynamodb", "sqlite", "sql", "snowflake",
    # AI / ML
    "machine learning", "deep learning", "nlp", "pytorch", "tensorflow", "keras", "hugging face", "transformers", "scikit-learn", "pandas", "numpy", "opencv", "computer vision", "yolo", "llm", "vector databases", "embeddings",
    # Architecture & Concepts
    "distributed systems", "microservices", "rest api", "graphql", "grpc", "system design", "performance optimization", "agile", "scrum", "git"
}

DEGREE_PATTERNS = [
    r"\b(?:ph\.?d\.?|doctor\s+of\s+philosophy)\b",
    r"\b(?:m\.?s\.?|master(?:\'?s)?(?:\s+of\s+science)?|m\.?tech\.?|m\.?c\.?a\.?|m\.?b\.?a\.?)\b",
    r"\b(?:b\.?s\.?|bachelor(?:\'?s)?(?:\s+of\s+science)?|b\.?tech\.?|b\.?e\.?|b\.?c\.?a\.?)\b",
    r"\b(?:associate(?:\'?s)?\s+degree|diploma)\b"
]

def extract_text_from_file(file_bytes: bytes, filename: str) -> Tuple[str, Optional[str]]:
    """
    Extracts text from PDF, DOCX, or TXT bytes.
    Returns (extracted_text, error_message).
    """
    fname_lower = filename.lower()
    text = ""
    error = None

    if fname_lower.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            if len(reader.pages) == 0:
                return "", "PDF file contains zero pages."
            
            pages_text = []
            for i, page in enumerate(reader.pages):
                pt = page.extract_text() or ""
                if pt.strip():
                    pages_text.append(pt.strip())
            
            text = "\n\n".join(pages_text).strip()
            if len(text) < 30:
                error = "Unreadable or scanned PDF document (no selectable text layer found). Scanned images require OCR."
        except Exception as e:
            error = f"Corrupted or invalid PDF file: {str(e)}"

    elif fname_lower.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip() and cell.text.strip() not in paragraphs:
                            paragraphs.append(cell.text.strip())
            text = "\n".join(paragraphs).strip()
            if len(text) < 20:
                error = "DOCX document appears empty or unreadable."
        except Exception as e:
            error = f"Corrupted or invalid DOCX file: {str(e)}"

    elif fname_lower.endswith(".txt"):
        try:
            text = file_bytes.decode("utf-8").strip()
        except UnicodeDecodeError:
            try:
                text = file_bytes.decode("latin-1", errors="ignore").strip()
            except Exception as e:
                error = f"Cannot decode text file: {str(e)}"
    else:
        error = f"Unsupported file extension '{fname_lower.split('.')[-1]}'. Please upload PDF or DOCX files."

    return text, error

def parse_email(text: str) -> Optional[str]:
    match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    if match:
        return match.group(0).lower().rstrip('.')
    return None

def parse_phone(text: str) -> Optional[str]:
    match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    if match:
        return match.group(0).strip()
    return None

def parse_name(text: str, filename: str) -> str:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:6]:
        # Filter out email, phone, web links, common headings
        if "@" in line or "http" in line or "www" in line:
            continue
        if re.search(r'\d{3}[-.\s]?\d{3}', line):
            continue
        if re.search(r'\b(resume|curriculum vitae|cv|summary|objective|experience|contact)\b', line, re.I):
            continue
        cleaned = re.sub(r'[^a-zA-Z\s\.\-]', '', line).strip()
        words = cleaned.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
            return cleaned.title()
    
    # Fallback to filename
    base_name = Path(filename).stem
    cleaned_fn = re.sub(r'[_+\-\.]', ' ', base_name)
    cleaned_fn = re.sub(r'\b(resume|cv|latest|2024|2025|2026)\b', '', cleaned_fn, flags=re.I).strip()
    if len(cleaned_fn) >= 3:
        return cleaned_fn.title()
    return "Candidate " + str(int(datetime.utcnow().timestamp()) % 1000)

def parse_experience_years(text: str) -> float:
    # Pattern 1: "X+ years", "X years of experience"
    exp_matches = re.findall(r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience)?', text, re.I)
    valid_years = []
    for m in exp_matches:
        try:
            val = float(m)
            if 0.5 <= val <= 35:
                valid_years.append(val)
        except ValueError:
            pass
    if valid_years:
        return max(valid_years)

    # Pattern 2: Detect date ranges e.g. 2018 - 2024 or 2019 - Present
    current_year = datetime.utcnow().year
    date_ranges = re.findall(r'\b(20\d\d|19\d\d)\s*(?:-|to|–|—)\s*(20\d\d|present|current)\b', text, re.I)
    total_span = 0.0
    for start, end in date_ranges:
        try:
            s_year = int(start)
            e_year = current_year if end.lower() in ["present", "current"] else int(end)
            diff = e_year - s_year
            if 0 < diff <= 35:
                total_span += diff
        except ValueError:
            pass
    if total_span > 0:
        return min(round(total_span, 1), 25.0)

    return 3.0  # sensible default baseline

def parse_education(text: str) -> str:
    lines = text.split("\n")
    found_degrees = []
    for line in lines:
        for pat in DEGREE_PATTERNS:
            if re.search(pat, line, re.I):
                deg = line.strip()
                if len(deg) <= 120 and deg not in found_degrees:
                    found_degrees.append(deg)
                break
    if found_degrees:
        return " | ".join(found_degrees[:2])
    
    # Generic fallback search
    if re.search(r'\b(bachelor|master|doctorate|b\.?s|m\.?s|b\.?tech)\b', text, re.I):
        return "B.S. in Computer Science or Related Technical Field"
    return "Higher Education Degree"

def parse_skills(text: str) -> List[str]:
    text_lower = text.lower()
    detected = []
    for skill in TECH_SKILLS_TAXONOMY:
        escaped = re.escape(skill)
        if re.search(r'\b' + escaped + r'\b', text_lower):
            display = skill.title()
            if skill in ["aws", "gcp", "sql", "nlp", "llm", "k8s", "ci/cd", "rest api", "graphql", "grpc"]:
                display = skill.upper()
            elif skill == "react.js":
                display = "React"
            elif skill == "node.js":
                display = "Node.js"
            elif skill == "pytorch":
                display = "PyTorch"
            elif skill == "fastapi":
                display = "FastAPI"
            elif skill == "postgresql" or skill == "postgres":
                display = "PostgreSQL"
            elif skill == "golang" or skill == "go":
                display = "Go"
            if display not in detected:
                detected.append(display)
    return detected[:15]

def evaluate_resume_against_job(
    parsed_candidate: Dict[str, Any],
    job: Dict[str, Any],
    selected_threshold: float = 70.0,
    maybe_threshold: float = 50.0,
    nlp_engine = None,
    resume_engine = None,
    resume_emb = None,
    jd_emb = None
) -> Dict[str, Any]:
    """
    Computes match score (0-100), decision status (Selected, Maybe, Rejected),
    matched skills, missing skills, and detailed AI reasoning.
    Accepts precomputed resume_emb and jd_emb for blazing-fast batch performance.
    """
    resume_text = parsed_candidate.get("raw_text", "")
    cand_skills = [s.lower() for s in parsed_candidate.get("skills", [])]
    
    # Required skills from job
    req_skills_raw = job.get("required_skills", [])
    if isinstance(req_skills_raw, str):
        import json
        try:
            req_skills = json.loads(req_skills_raw)
        except Exception:
            req_skills = [s.strip() for s in req_skills_raw.split(",") if s.strip()]
    else:
        req_skills = list(req_skills_raw)

    matched_skills = []
    missing_skills = []
    resume_text_lower = resume_text.lower()

    for skill in req_skills:
        s_lower = skill.lower()
        # Direct check in cand_skills or in raw resume text
        if s_lower in cand_skills or re.search(r'\b' + re.escape(s_lower) + r'\b', resume_text_lower):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    # Keyword / Skills Match Score (0 - 100)
    skill_ratio = (len(matched_skills) / len(req_skills)) if req_skills else 1.0
    keyword_score = round(skill_ratio * 100.0, 1)

    # Experience alignment (0 - 100)
    min_exp = float(job.get("experience_required", 3.0))
    cand_exp = float(parsed_candidate.get("experience_years", 3.0))
    if cand_exp >= min_exp:
        exp_score = min(100.0, 85.0 + ((cand_exp - min_exp) * 3.0))
    else:
        ratio = max(0.2, cand_exp / max(min_exp, 1.0))
        exp_score = round(ratio * 75.0, 1)

    # Semantic similarity score (fast path with precomputed embeddings)
    semantic_score = keyword_score  # fallback
    if resume_emb is not None and jd_emb is not None and nlp_engine and hasattr(nlp_engine, "compute_semantic_similarity_with_embeddings"):
        semantic_score = nlp_engine.compute_semantic_similarity_with_embeddings(jd_emb, resume_emb)
    elif nlp_engine and hasattr(nlp_engine, "compute_semantic_similarity"):
        try:
            jd_desc = job.get("description", "") + " " + " ".join(req_skills)
            semantic_score = nlp_engine.compute_semantic_similarity(jd_desc, resume_text)
        except Exception:
            semantic_score = keyword_score

    # Weighted composite score (40% skills, 40% semantic, 20% experience)
    overall_score = round(
        (keyword_score * 0.40) + (semantic_score * 0.40) + (exp_score * 0.20),
        1
    )
    overall_score = max(5.0, min(99.0, overall_score))

    # Determine status
    if overall_score >= selected_threshold:
        status = "Selected"
    elif overall_score >= maybe_threshold:
        status = "Maybe"
    else:
        status = "Rejected"

    # Connected models classification (fast path with precomputed embedding)
    model_predictions = {}
    if resume_emb is not None and resume_engine and hasattr(resume_engine, "classify_with_embedding"):
        try:
            model_predictions = resume_engine.classify_with_embedding(resume_emb)
        except Exception:
            pass
    elif resume_engine and hasattr(resume_engine, "classify_all_models"):
        try:
            model_predictions = resume_engine.classify_all_models(resume_text)
        except Exception:
            pass

    # Construct concise, explainable reasoning
    matched_str = ", ".join(matched_skills) if matched_skills else "None"
    missing_str = ", ".join(missing_skills) if missing_skills else "None"
    
    if status == "Selected":
        reason = f"Excellent match ({overall_score}%). Matched {len(matched_skills)}/{len(req_skills)} required skills ({matched_str}). Candidate brings {cand_exp} yrs experience (vs {min_exp} yrs required) with strong semantic alignment ({semantic_score}%)."
    elif status == "Maybe":
        reason = f"Moderate match ({overall_score}%). Matched {len(matched_skills)}/{len(req_skills)} skills ({matched_str}), but missing: {missing_str}. Has {cand_exp} yrs experience. Suitable for secondary interview review."
    else:
        reason = f"Low match ({overall_score}%). Missing critical required skills: {missing_str}. Experience ({cand_exp} yrs) and domain alignment did not meet the {selected_threshold}% selection threshold."

    return {
        "overall_score": overall_score,
        "status": status,
        "decision_reason": reason,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "score_breakdown": {
            "skills_overlap": keyword_score,
            "semantic_match": semantic_score,
            "experience_alignment": exp_score
        },
        "model_predictions": model_predictions
    }
