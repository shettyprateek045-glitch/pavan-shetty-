"""
Seed initial screening database with realistic candidates and screening results.
"""

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
import uuid
from datetime import datetime, timedelta
from backend.database import get_connection
from backend.synthetic_data import CANDIDATES_DATABASE
from backend.resume_parser import evaluate_resume_against_job, parse_skills, parse_experience_years, parse_education
import backend.nlp_engine as nlp_engine

try:
    from backend.resume_service import resume_engine
except ImportError:
    resume_engine = None

def seed_screenings():
    conn = get_connection()
    cursor = conn.cursor()

    # Check existing count
    cursor.execute("SELECT count(*) as count FROM screenings WHERE recruiter_id = 'recruiter-default'")
    if cursor.fetchone()["count"] > 0:
        conn.close()
        return

    cursor.execute("SELECT * FROM jobs WHERE recruiter_id = 'recruiter-default'")
    job_rows = cursor.fetchall()
    if not job_rows:
        conn.close()
        return

    jobs = [dict(r) for r in job_rows]
    for j in jobs:
        try:
            j["required_skills"] = json.loads(j["required_skills"])
        except Exception:
            j["required_skills"] = [s.strip() for s in j["required_skills"].split(",") if s.strip()]

    now = datetime.utcnow()

    # Seed candidates
    for i, c in enumerate(CANDIDATES_DATABASE[:15]):
        cand_id = f"cand-seed-{i+1:02d}"
        recruiter_id = "recruiter-default"
        name = c["name"]
        email = c.get("email", f"{name.lower().replace(' ', '.')}@example.com")
        phone = c.get("phone", f"+1 (555) 01{i+1:02d}-4920")
        raw_text = c.get("resume_text", "")
        skills = c.get("skills", parse_skills(raw_text))
        exp_years = float(c.get("experience_years", parse_experience_years(raw_text)))
        education = c.get("education", parse_education(raw_text))
        filename = f"{name.replace(' ', '_')}_Resume.pdf"

        cand_created = (now - timedelta(days=14 - i)).isoformat()

        cursor.execute("""
        INSERT OR REPLACE INTO candidates (
            id, recruiter_id, name, email, phone, skills, experience_years,
            education, raw_text, original_filename, file_type, file_size, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cand_id,
            recruiter_id,
            name,
            email,
            phone,
            json.dumps(skills),
            exp_years,
            education,
            raw_text,
            filename,
            "pdf",
            48291 + (i * 1234),
            cand_created
        ))

        # Assign to a job
        assigned_job = jobs[i % len(jobs)]
        eval_res = evaluate_resume_against_job(
            {"name": name, "skills": skills, "experience_years": exp_years, "raw_text": raw_text},
            assigned_job,
            selected_threshold=70.0,
            maybe_threshold=50.0,
            nlp_engine=nlp_engine,
            resume_engine=resume_engine
        )

        scr_id = f"scr-seed-{i+1:02d}"
        scr_created = (now - timedelta(days=14 - i, hours=i)).isoformat()

        cursor.execute("""
        INSERT OR REPLACE INTO screenings (
            id, candidate_id, job_id, recruiter_id, score, status, decision_reason,
            matched_skills, missing_skills, score_breakdown, model_predictions,
            manual_override, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
        """, (
            scr_id,
            cand_id,
            assigned_job["id"],
            recruiter_id,
            eval_res["overall_score"],
            eval_res["status"],
            eval_res["decision_reason"],
            json.dumps(eval_res["matched_skills"]),
            json.dumps(eval_res["missing_skills"]),
            json.dumps(eval_res["score_breakdown"]),
            json.dumps(eval_res["model_predictions"]),
            scr_created
        ))

    conn.commit()
    conn.close()
    print("Screening database seeded successfully with realistic candidates and screening results.")

if __name__ == "__main__":
    seed_screenings()
