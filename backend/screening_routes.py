"""
AI Resume Screening Router
==========================
Endpoints for:
1. Job management (pick or create jobs)
2. Resume file ingestion (PDF, DOCX) & batch scanning
3. Configurable scoring (Selected >= 70, Maybe 50-69, Rejected < 50)
4. Dashboard summary KPIs, candidate table, and analytics charts
5. Detailed candidate resume breakdown & AI reasoning
6. Permanent screening history & manual decision overrides
7. Multi-recruiter privacy isolation and duplicate detection
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Header, Query
from pydantic import BaseModel, Field

from backend.database import get_connection
from backend.resume_parser import (
    extract_text_from_file,
    parse_email,
    parse_phone,
    parse_name,
    parse_skills,
    parse_experience_years,
    parse_education,
    evaluate_resume_against_job
)
import backend.nlp_engine as nlp_engine

try:
    from backend.resume_service import resume_engine
except ImportError:
    resume_engine = None

router = APIRouter(prefix="/api/screening", tags=["AI Resume Screening"])

# Pydantic Schemas
class JobCreatePayload(BaseModel):
    title: str
    required_skills: List[str]
    experience_required: float = 3.0
    description: str
    company: Optional[str] = "TalentRank Systems"
    department: Optional[str] = "Engineering"
    location: Optional[str] = "San Francisco, CA / Remote"
    salary_range: Optional[str] = "$140,000 - $190,000"
    nice_to_have_skills: Optional[List[str]] = []
    recruiter_id: Optional[str] = "recruiter-default"

class ManualOverridePayload(BaseModel):
    screening_id: str
    new_status: str
    override_by: str = "Jordan Davis"
    override_reason: Optional[str] = "Recruiter manual assessment based on portfolio"

class SettingsPayload(BaseModel):
    recruiter_id: Optional[str] = "recruiter-default"
    selected_threshold: float = 70.0
    maybe_threshold: float = 50.0
    blind_screening: Optional[int] = 0

class RescreenPayload(BaseModel):
    screening_id: str
    job_id: Optional[str] = None
    recruiter_id: Optional[str] = "recruiter-default"
    selected_threshold: Optional[float] = None
    maybe_threshold: Optional[float] = None

def get_current_recruiter_id(recruiter_id_header: Optional[str] = Header(None, alias="X-Recruiter-Id")) -> str:
    if recruiter_id_header and recruiter_id_header.strip():
        return recruiter_id_header.strip()
    return "recruiter-default"

# -------------------------------------------------------------------------
# 1. Job Management (Pick or Create)
# -------------------------------------------------------------------------
@router.get("/jobs")
def get_recruiter_jobs(recruiter_id: str = Query("recruiter-default")):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM jobs 
        WHERE recruiter_id = ? OR recruiter_id = 'recruiter-default'
        ORDER BY created_at DESC
    """, (recruiter_id,))
    rows = cursor.fetchall()
    jobs = []
    for r in rows:
        j = dict(r)
        try:
            j["required_skills"] = json.loads(j["required_skills"])
        except Exception:
            j["required_skills"] = [s.strip() for s in j["required_skills"].split(",") if s.strip()]
        try:
            j["nice_to_have_skills"] = json.loads(j["nice_to_have_skills"]) if j["nice_to_have_skills"] else []
        except Exception:
            j["nice_to_have_skills"] = []
        jobs.append(j)
    conn.close()
    return {"jobs": jobs}

@router.post("/jobs")
def create_job(payload: JobCreatePayload):
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail="Job title is required.")
    if not payload.required_skills:
        raise HTTPException(status_code=400, detail="At least one required skill is required.")

    conn = get_connection()
    cursor = conn.cursor()
    job_id = f"job-{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().isoformat()

    cursor.execute("""
    INSERT INTO jobs (
        id, recruiter_id, title, company, department, location,
        experience_required, salary_range, required_skills, nice_to_have_skills,
        description, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job_id,
        payload.recruiter_id or "recruiter-default",
        payload.title.strip(),
        payload.company or "TalentRank Systems",
        payload.department or "Engineering",
        payload.location or "San Francisco, CA / Remote",
        payload.experience_required,
        payload.salary_range or "$140,000 - $190,000",
        json.dumps(payload.required_skills),
        json.dumps(payload.nice_to_have_skills or []),
        payload.description.strip(),
        "Active",
        now
    ))
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "message": f"Job posting '{payload.title}' created successfully.",
        "job": {
            "id": job_id,
            "title": payload.title,
            "required_skills": payload.required_skills,
            "experience_required": payload.experience_required,
            "description": payload.description
        }
    }

# -------------------------------------------------------------------------
# 2. Resume Upload & Automatic Screening
# -------------------------------------------------------------------------
@router.post("/upload")
async def upload_and_screen_resumes(
    files: List[UploadFile] = File(...),
    job_id: str = Form(...),
    recruiter_id: str = Form("recruiter-default"),
    selected_threshold: Optional[float] = Form(70.0),
    maybe_threshold: Optional[float] = Form(50.0)
):
    if not files:
        raise HTTPException(status_code=400, detail="No resume files uploaded.")

    conn = get_connection()
    cursor = conn.cursor()

    # Retrieve selected job
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    job_row = cursor.fetchone()
    if not job_row:
        # Fallback to first available job
        cursor.execute("SELECT * FROM jobs LIMIT 1")
        job_row = cursor.fetchone()
        if not job_row:
            conn.close()
            raise HTTPException(status_code=404, detail="No job posting found. Please create a job first.")

    job = dict(job_row)
    try:
        job["required_skills"] = json.loads(job["required_skills"])
    except Exception:
        job["required_skills"] = [s.strip() for s in job["required_skills"].split(",") if s.strip()]

    # Fetch recruiter configured thresholds if not explicitly provided
    if selected_threshold is None or maybe_threshold is None:
        cursor.execute("SELECT selected_threshold, maybe_threshold FROM recruiter_settings WHERE recruiter_id = ?", (recruiter_id,))
        settings_row = cursor.fetchone()
        if settings_row:
            selected_threshold = selected_threshold or settings_row["selected_threshold"]
            maybe_threshold = maybe_threshold or settings_row["maybe_threshold"]
        else:
            selected_threshold = selected_threshold or 70.0
            maybe_threshold = maybe_threshold or 50.0

    conn.close()

    # Pre-encode Job Description embedding once for blazing-fast batch screening
    jd_desc = job.get("description", "") + " " + " ".join(job.get("required_skills", []))
    jd_emb = None
    if resume_engine and hasattr(resume_engine, "get_embedding"):
        try:
            jd_emb = resume_engine.get_embedding(jd_desc)
        except Exception:
            jd_emb = None

    processed_candidates = []
    errors = []
    now = datetime.utcnow().isoformat()

    import hashlib

    for file in files:
        filename = file.filename or "uploaded_resume.pdf"
        try:
            file_bytes = await file.read()
            file_size = len(file_bytes)
            file_ext = filename.split(".")[-1].lower() if "." in filename else "unknown"
            file_hash = hashlib.sha256(file_bytes).hexdigest()

            # 1. Text Extraction
            extracted_text, extraction_error = extract_text_from_file(file_bytes, filename)
            if extraction_error:
                errors.append({
                    "filename": filename,
                    "error": extraction_error,
                    "status": "Failed"
                })
                continue

            # 2. Entity Parsing
            email = parse_email(extracted_text) or f"cand.{file_hash[:8]}@screening.ai"
            phone = parse_phone(extracted_text) or "+1 (555) 019-2834"
            name = parse_name(extracted_text, filename)
            skills = parse_skills(extracted_text)
            exp_years = parse_experience_years(extracted_text)
            education = parse_education(extracted_text)

            # 3. Security & Fraud Check ("Resumes are data, never orders") - in-memory
            from backend.security_defender import analyze_pdf_security, analyze_raw_text_security
            try:
                if file_ext == "pdf":
                    sec_report = analyze_pdf_security(file_bytes)
                else:
                    sec_report = analyze_raw_text_security(extracted_text)
            except Exception as sec_e:
                sec_report = {
                    "is_fraud": False,
                    "reason": f"Security check fallback: {str(sec_e)}",
                    "evidence": [],
                    "flagged_orders": []
                }

            is_fraud = sec_report.get("is_fraud", False)
            fraud_reason = sec_report.get("fraud_reason") or sec_report.get("reason")
            flagged_orders = sec_report.get("flagged_orders", [])

            # 4. Evaluation against Job Requirements - in-memory (with fast precomputed embeddings)
            candidate_obj = {
                "name": name,
                "skills": skills,
                "experience_years": exp_years,
                "raw_text": extracted_text
            }
            res_emb = None
            if resume_engine and hasattr(resume_engine, "get_embedding"):
                try:
                    res_emb = resume_engine.get_embedding(extracted_text)
                except Exception:
                    res_emb = None

            eval_result = evaluate_resume_against_job(
                candidate_obj,
                job,
                selected_threshold=selected_threshold,
                maybe_threshold=maybe_threshold,
                nlp_engine=nlp_engine,
                resume_engine=resume_engine,
                resume_emb=res_emb,
                jd_emb=jd_emb
            )

            # If fraud (orders detected), mark status as FRAUD and remove from shortlist
            final_status = "FRAUD" if is_fraud else eval_result["status"]
            in_shortlist = False if is_fraud else (final_status == "Selected")
            decision_reason = f"🚨 FRAUD DETECTED: Resumes are data, never orders. {fraud_reason}" if is_fraud else eval_result["decision_reason"]

            # 5. Multi-Agent Evaluations (Entities, Alignment, Anomalies, Interview Questions) - in-memory
            from backend.multi_agent_pipeline import run_multi_agent_evaluation
            try:
                agent_eval = run_multi_agent_evaluation(
                    resume_text=extracted_text,
                    required_skills=job["required_skills"],
                    jd_text=job.get("description", ""),
                    file_bytes=file_bytes if file_ext == "pdf" else None,
                    file_type=file_ext,
                    security_report=sec_report
                )
            except Exception as agent_e:
                agent_eval = {
                    "security_defender": sec_report,
                    "entity_evidence": {},
                    "deep_alignment": {},
                    "anomaly_review": {},
                    "interview_questions": []
                }

            # 6. Database Storage with atomic commit (fast lock window)
            screening_id = f"scr-{uuid.uuid4().hex[:8]}"
            is_duplicate = False

            save_conn = get_connection()
            try:
                save_cursor = save_conn.cursor()

                # Duplicate check by file_hash OR email
                save_cursor.execute(
                    "SELECT id, name FROM candidates WHERE recruiter_id = ? AND (file_hash = ? OR email = ?)",
                    (recruiter_id, file_hash, email)
                )
                existing_candidate = save_cursor.fetchone()

                if existing_candidate:
                    is_duplicate = True
                    candidate_id = existing_candidate["id"]
                    save_cursor.execute("""
                    UPDATE candidates 
                    SET raw_text = ?, skills = ?, experience_years = ?, education = ?, original_filename = ?, file_type = ?, file_size = ?, file_hash = ?
                    WHERE id = ?
                    """, (
                        extracted_text,
                        json.dumps(skills),
                        exp_years,
                        education,
                        filename,
                        file_ext,
                        file_size,
                        file_hash,
                        candidate_id
                    ))
                else:
                    candidate_id = f"cand-{uuid.uuid4().hex[:8]}"
                    save_cursor.execute("""
                    INSERT INTO candidates (
                        id, recruiter_id, name, email, phone, skills, experience_years,
                        education, raw_text, original_filename, file_type, file_size, file_hash, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        candidate_id,
                        recruiter_id,
                        name,
                        email,
                        phone,
                        json.dumps(skills),
                        exp_years,
                        education,
                        extracted_text,
                        filename,
                        file_ext,
                        file_size,
                        file_hash,
                        now
                    ))

                # Screening record
                save_cursor.execute("""
                INSERT INTO screenings (
                    id, candidate_id, job_id, recruiter_id, score, status, decision_reason,
                    matched_skills, missing_skills, score_breakdown, model_predictions,
                    manual_override, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                """, (
                    screening_id,
                    candidate_id,
                    job["id"],
                    recruiter_id,
                    eval_result["overall_score"],
                    final_status,
                    decision_reason,
                    json.dumps(eval_result["matched_skills"]),
                    json.dumps(eval_result["missing_skills"]),
                    json.dumps(eval_result["score_breakdown"]),
                    json.dumps(eval_result["model_predictions"]),
                    now
                ))

                # Agent evaluations
                save_cursor.execute("""
                INSERT OR REPLACE INTO agent_evaluations (
                    screening_id, security_report, entities_report, alignment_report,
                    anomalies_report, interview_questions, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    screening_id,
                    json.dumps(agent_eval.get("security_defender", sec_report)),
                    json.dumps(agent_eval.get("entity_evidence", {})),
                    json.dumps(agent_eval.get("deep_alignment", {})),
                    json.dumps(agent_eval.get("anomaly_review", {})),
                    json.dumps(agent_eval.get("interview_questions", [])),
                    now
                ))

                save_conn.commit()
            finally:
                save_conn.close()

            processed_candidates.append({
                "screening_id": screening_id,
                "candidate_id": candidate_id,
                "name": name,
                "email": email,
                "phone": phone,
                "filename": filename,
                "job_title": job["title"],
                "score": eval_result["overall_score"],
                "status": final_status,
                "in_shortlist": in_shortlist,
                "decision_reason": decision_reason,
                "matched_skills": eval_result["matched_skills"],
                "missing_skills": eval_result["missing_skills"],
                "score_breakdown": eval_result["score_breakdown"],
                "model_predictions": eval_result["model_predictions"],
                "is_duplicate": is_duplicate,
                "is_fraud": is_fraud,
                "fraud_label": "FRAUD - Attempted to give orders to the screening system" if is_fraud else None,
                "fraud_reason": fraud_reason,
                "evidence": sec_report.get("evidence", flagged_orders),
                "flagged_orders": flagged_orders,
                "created_at": now
            })

        except Exception as file_exc:
            import traceback
            traceback.print_exc()
            errors.append({
                "filename": filename,
                "error": str(file_exc),
                "status": "Failed"
            })

    return {
        "status": "success",
        "total_uploaded": len(files),
        "total_processed": len(processed_candidates),
        "total_errors": len(errors),
        "errors": errors,
        "job_evaluated": job["title"],
        "candidates": processed_candidates
    }

# -------------------------------------------------------------------------
# 3. Screening Dashboard View & Analytics
# -------------------------------------------------------------------------
@router.get("/dashboard")
def get_screening_dashboard(
    recruiter_id: str = Query("recruiter-default"),
    job_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("score_desc")
):
    conn = get_connection()
    cursor = conn.cursor()

    # Query all screenings for recruiter
    query = """
    SELECT 
        s.id AS screening_id,
        s.score,
        s.status,
        s.decision_reason,
        s.matched_skills,
        s.missing_skills,
        s.score_breakdown,
        s.model_predictions,
        s.manual_override,
        s.override_by,
        s.override_reason,
        s.override_timestamp,
        s.created_at AS screening_date,
        c.id AS candidate_id,
        c.name AS candidate_name,
        c.email AS candidate_email,
        c.phone AS candidate_phone,
        c.skills AS candidate_skills,
        c.experience_years,
        c.education,
        c.original_filename,
        j.id AS job_id,
        j.title AS job_title,
        ae.security_report
    FROM screenings s
    JOIN candidates c ON s.candidate_id = c.id
    JOIN jobs j ON s.job_id = j.id
    LEFT JOIN agent_evaluations ae ON s.id = ae.screening_id
    WHERE s.recruiter_id = ?
    """
    params = [recruiter_id]

    if job_id and job_id != "all":
        query += " AND s.job_id = ?"
        params.append(job_id)

    if status and status != "all":
        query += " AND s.status = ?"
        params.append(status)

    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        query += " AND (LOWER(c.name) LIKE ? OR LOWER(c.email) LIKE ? OR LOWER(j.title) LIKE ?)"
        params.extend([term, term, term])

    # Sorting
    if sort_by == "score_asc":
        query += " ORDER BY s.score ASC"
    elif sort_by == "date_desc":
        query += " ORDER BY s.created_at DESC"
    elif sort_by == "name_asc":
        query += " ORDER BY c.name ASC"
    else:
        # Default: score_desc
        query += " ORDER BY s.score DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    candidates_list = []
    for r in rows:
        item = dict(r)
        try:
            item["matched_skills"] = json.loads(item["matched_skills"]) if item["matched_skills"] else []
        except Exception:
            item["matched_skills"] = []
        try:
            item["missing_skills"] = json.loads(item["missing_skills"]) if item["missing_skills"] else []
        except Exception:
            item["missing_skills"] = []
        try:
            item["score_breakdown"] = json.loads(item["score_breakdown"]) if item["score_breakdown"] else {}
        except Exception:
            item["score_breakdown"] = {}
        try:
            item["model_predictions"] = json.loads(item["model_predictions"]) if item["model_predictions"] else {}
        except Exception:
            item["model_predictions"] = {}
        try:
            item["candidate_skills"] = json.loads(item["candidate_skills"]) if item["candidate_skills"] else []
        except Exception:
            item["candidate_skills"] = []
        try:
            sec_obj = json.loads(item.get("security_report") or "{}")
            item["is_fraud"] = sec_obj.get("is_fraud", False)
            item["fraud_orders"] = sec_obj.get("flagged_orders", [])
            item["fraud_reason"] = sec_obj.get("fraud_reason")
        except Exception:
            item["is_fraud"] = False
            item["fraud_orders"] = []
        candidates_list.append(item)

    # Calculate overall summary metrics across recruiter's screenings (unfiltered by status for KPI accuracy)
    cursor.execute("""
    SELECT 
        COUNT(*) AS total_scanned,
        SUM(CASE WHEN status = 'Selected' THEN 1 ELSE 0 END) AS selected_count,
        SUM(CASE WHEN status = 'Maybe' THEN 1 ELSE 0 END) AS maybe_count,
        SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) AS rejected_count,
        AVG(score) AS avg_score
    FROM screenings
    WHERE recruiter_id = ?
    """, (recruiter_id,))
    kpi_row = cursor.fetchone()

    total_scanned = kpi_row["total_scanned"] or 0
    selected_count = kpi_row["selected_count"] or 0
    maybe_count = kpi_row["maybe_count"] or 0
    rejected_count = kpi_row["rejected_count"] or 0
    avg_score = round(kpi_row["avg_score"] or 0.0, 1)

    # Applications per job (for Bar chart)
    cursor.execute("""
    SELECT j.title AS job_title, COUNT(s.id) AS count
    FROM screenings s
    JOIN jobs j ON s.job_id = j.id
    WHERE s.recruiter_id = ?
    GROUP BY j.id
    ORDER BY count DESC
    LIMIT 6
    """, (recruiter_id,))
    app_rows = cursor.fetchall()
    apps_per_job = [{"job_title": r["job_title"], "count": r["count"]} for r in app_rows]

    conn.close()

    return {
        "summary": {
            "total_scanned": total_scanned,
            "selected": selected_count,
            "maybe": maybe_count,
            "rejected": rejected_count,
            "average_score": avg_score
        },
        "charts": {
            "status_split": [
                {"name": "Selected", "count": selected_count, "color": "#16A34A"},
                {"name": "Maybe", "count": maybe_count, "color": "#EAB308"},
                {"name": "Rejected", "count": rejected_count, "color": "#EF4444"}
            ],
            "applications_per_job": apps_per_job
        },
        "candidates": candidates_list
    }

# -------------------------------------------------------------------------
# 4. Candidate Detail Profile & AI Reasoning
# -------------------------------------------------------------------------
@router.get("/candidates/{screening_id}")
def get_candidate_detail(screening_id: str, recruiter_id: str = Query("recruiter-default")):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        s.id AS screening_id,
        s.score,
        s.status,
        s.decision_reason,
        s.matched_skills,
        s.missing_skills,
        s.score_breakdown,
        s.model_predictions,
        s.manual_override,
        s.override_by,
        s.override_reason,
        s.override_timestamp,
        s.created_at AS screening_date,
        c.id AS candidate_id,
        c.name AS candidate_name,
        c.email AS candidate_email,
        c.phone AS candidate_phone,
        c.skills AS candidate_skills,
        c.experience_years,
        c.education,
        c.raw_text,
        c.original_filename,
        c.file_type,
        c.file_size,
        j.id AS job_id,
        j.title AS job_title,
        j.experience_required AS job_experience_required,
        j.required_skills AS job_required_skills,
        j.description AS job_description
    FROM screenings s
    JOIN candidates c ON s.candidate_id = c.id
    JOIN jobs j ON s.job_id = j.id
    WHERE s.id = ? AND s.recruiter_id = ?
    """, (screening_id, recruiter_id))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Screening record not found.")

    res = dict(row)
    for field in ["matched_skills", "missing_skills", "score_breakdown", "model_predictions", "candidate_skills", "job_required_skills"]:
        try:
            res[field] = json.loads(res[field]) if res.get(field) else []
        except Exception:
            pass

    return res

# -------------------------------------------------------------------------
# 5. Manual Decision Override & Audit Logging
# -------------------------------------------------------------------------
@router.post("/override")
def override_screening_decision(payload: ManualOverridePayload):
    if payload.new_status not in ["Selected", "Maybe", "Rejected"]:
        raise HTTPException(status_code=400, detail="Status must be 'Selected', 'Maybe', or 'Rejected'.")

    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()

    cursor.execute("SELECT id FROM screenings WHERE id = ?", (payload.screening_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Screening record not found.")

    cursor.execute("""
    UPDATE screenings 
    SET 
        status = ?,
        manual_override = 1,
        override_by = ?,
        override_reason = ?,
        override_timestamp = ?
    WHERE id = ?
    """, (
        payload.new_status,
        payload.override_by,
        payload.override_reason or "Manual recruiter assessment",
        now,
        payload.screening_id
    ))
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "message": f"Decision successfully overridden to '{payload.new_status}'.",
        "override_details": {
            "screening_id": payload.screening_id,
            "new_status": payload.new_status,
            "override_by": payload.override_by,
            "override_timestamp": now
        }
    }

# -------------------------------------------------------------------------
# 6. Screening History & Re-screen
# -------------------------------------------------------------------------
@router.get("/history")
def get_screening_history(recruiter_id: str = Query("recruiter-default")):
    conn = get_connection()
    cursor = conn.cursor()

    # Past Screenings
    cursor.execute("""
    SELECT 
        s.id AS screening_id,
        s.score,
        s.status,
        s.decision_reason,
        s.matched_skills,
        s.missing_skills,
        s.manual_override,
        s.override_by,
        s.override_reason,
        s.override_timestamp,
        s.created_at,
        c.name AS candidate_name,
        c.email AS candidate_email,
        c.original_filename,
        c.experience_years,
        j.title AS job_title
    FROM screenings s
    JOIN candidates c ON s.candidate_id = c.id
    JOIN jobs j ON s.job_id = j.id
    WHERE s.recruiter_id = ?
    ORDER BY s.created_at DESC
    """, (recruiter_id,))
    screenings = [dict(r) for r in cursor.fetchall()]

    for item in screenings:
        try:
            item["matched_skills"] = json.loads(item["matched_skills"]) if item["matched_skills"] else []
        except Exception:
            item["matched_skills"] = []
        try:
            item["missing_skills"] = json.loads(item["missing_skills"]) if item["missing_skills"] else []
        except Exception:
            item["missing_skills"] = []

    # Past Job Postings
    cursor.execute("""
    SELECT j.*, COUNT(s.id) AS applications_count
    FROM jobs j
    LEFT JOIN screenings s ON j.id = s.job_id
    WHERE j.recruiter_id = ? OR j.recruiter_id = 'recruiter-default'
    GROUP BY j.id
    ORDER BY j.created_at DESC
    """, (recruiter_id,))
    jobs = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "history": screenings,
        "job_postings": jobs
    }

@router.post("/rescreen")
def rescreen_candidate(payload: RescreenPayload):
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch original screening & candidate
    cursor.execute("""
    SELECT s.*, c.raw_text, c.name, c.skills, c.experience_years
    FROM screenings s
    JOIN candidates c ON s.candidate_id = c.id
    WHERE s.id = ?
    """, (payload.screening_id,))
    record = cursor.fetchone()
    if not record:
        conn.close()
        raise HTTPException(status_code=404, detail="Screening record not found.")

    target_job_id = payload.job_id or record["job_id"]
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (target_job_id,))
    job_row = cursor.fetchone()
    if not job_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Target job posting not found.")

    job = dict(job_row)
    try:
        job["required_skills"] = json.loads(job["required_skills"])
    except Exception:
        job["required_skills"] = [s.strip() for s in job["required_skills"].split(",") if s.strip()]

    # Candidate object
    cand_obj = {
        "name": record["name"],
        "skills": json.loads(record["skills"]) if record["skills"] else [],
        "experience_years": record["experience_years"],
        "raw_text": record["raw_text"]
    }

    selected_thr = payload.selected_threshold or 70.0
    maybe_thr = payload.maybe_threshold or 50.0

    eval_result = evaluate_resume_against_job(
        cand_obj,
        job,
        selected_threshold=selected_thr,
        maybe_threshold=maybe_thr,
        nlp_engine=nlp_engine,
        resume_engine=resume_engine
    )

    now = datetime.utcnow().isoformat()
    cursor.execute("""
    UPDATE screenings
    SET 
        job_id = ?,
        score = ?,
        status = ?,
        decision_reason = ?,
        matched_skills = ?,
        missing_skills = ?,
        score_breakdown = ?,
        model_predictions = ?,
        manual_override = 0,
        override_by = NULL,
        override_reason = NULL,
        override_timestamp = NULL,
        created_at = ?
    WHERE id = ?
    """, (
        target_job_id,
        eval_result["overall_score"],
        eval_result["status"],
        eval_result["decision_reason"],
        json.dumps(eval_result["matched_skills"]),
        json.dumps(eval_result["missing_skills"]),
        json.dumps(eval_result["score_breakdown"]),
        json.dumps(eval_result["model_predictions"]),
        now,
        payload.screening_id
    ))
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "message": f"Candidate re-screened against '{job['title']}'. New status: {eval_result['status']} ({eval_result['overall_score']}%)",
        "result": eval_result
    }

# -------------------------------------------------------------------------
# 7. Recruiter Threshold Settings
# -------------------------------------------------------------------------
@router.get("/settings")
def get_recruiter_settings(recruiter_id: str = Query("recruiter-default")):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recruiter_settings WHERE recruiter_id = ?", (recruiter_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {
            "recruiter_id": recruiter_id,
            "selected_threshold": 70.0,
            "maybe_threshold": 50.0,
            "blind_screening": 0
        }
    return dict(row)

@router.post("/settings")
def update_recruiter_settings(payload: SettingsPayload):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    recruiter_id = payload.recruiter_id or "recruiter-default"

    cursor.execute("""
    INSERT INTO recruiter_settings (recruiter_id, selected_threshold, maybe_threshold, blind_screening, updated_at)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(recruiter_id) DO UPDATE SET
        selected_threshold = excluded.selected_threshold,
        maybe_threshold = excluded.maybe_threshold,
        blind_screening = excluded.blind_screening,
        updated_at = excluded.updated_at
    """, (
        recruiter_id,
        payload.selected_threshold,
        payload.maybe_threshold,
        payload.blind_screening or 0,
        now
    ))
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "message": "Screening threshold settings updated successfully.",
        "settings": {
            "selected_threshold": payload.selected_threshold,
            "maybe_threshold": payload.maybe_threshold,
            "blind_screening": payload.blind_screening
        }
    }


# -------------------------------------------------------------------------
# 8. Bulk Async Batch Ingestion (ZIP, Folder, Multi-file)
# -------------------------------------------------------------------------
from backend.batch_queue import safe_extract_zip, create_batch_job, get_batch_job_status
from backend.copilot_engine import execute_copilot_search
from backend.multi_agent_pipeline import run_multi_agent_evaluation

class CopilotQueryPayload(BaseModel):
    query: str
    recruiter_id: Optional[str] = "recruiter-default"
    custom_filters: Optional[Dict[str, Any]] = None

class UpdateInterviewQuestionsPayload(BaseModel):
    screening_id: str
    questions: List[Dict[str, Any]]

@router.post("/batch/upload")
async def bulk_async_upload(
    files: List[UploadFile] = File(...),
    job_id: str = Form(...),
    recruiter_id: str = Form("recruiter-default"),
    selected_threshold: Optional[float] = Form(70.0),
    maybe_threshold: Optional[float] = Form(50.0)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    files_to_queue = []

    for f in files:
        filename = f.filename or "uploaded_file"
        file_bytes = await f.read()
        ext = filename.lower().split('.')[-1] if '.' in filename else ''

        if ext == 'zip':
            # Safely unpack ZIP with path traversal and zip bomb protection
            extracted_items, zip_error = safe_extract_zip(file_bytes)
            if zip_error:
                raise HTTPException(status_code=400, detail=f"ZIP validation error ({filename}): {zip_error}")
            files_to_queue.extend(extracted_items)
        elif ext in ['pdf', 'docx', 'txt']:
            files_to_queue.append({
                "filename": filename,
                "bytes": file_bytes,
                "size": len(file_bytes),
                "ext": ext
            })
        else:
            # Skip unsupported file extensions
            continue

    if not files_to_queue:
        raise HTTPException(status_code=400, detail="No valid PDF or DOCX resume documents found in upload payload.")

    batch_meta = create_batch_job(
        recruiter_id=recruiter_id,
        job_id=job_id,
        files_data=files_to_queue,
        selected_threshold=selected_threshold or 70.0,
        maybe_threshold=maybe_threshold or 50.0
    )

    return {
        "status": "queued",
        "message": f"Successfully queued batch job containing {len(files_to_queue)} resume document(s) for asynchronous multi-agent processing.",
        "batch_id": batch_meta["batch_id"],
        "total_files": len(files_to_queue),
        "polling_url": f"/api/screening/batch/{batch_meta['batch_id']}/status"
    }

@router.get("/batch/{batch_id}/status")
def get_batch_status(batch_id: str):
    status_data = get_batch_job_status(batch_id)
    if not status_data:
        raise HTTPException(status_code=404, detail="Batch job not found.")
    return status_data

# -------------------------------------------------------------------------
# 9. Multi-Agent Structured Evaluations & Evidence Scorecards
# -------------------------------------------------------------------------
@router.get("/evaluations/{screening_id}")
def get_agent_evaluations(screening_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM agent_evaluations WHERE screening_id = ?", (screening_id,))
    row = cursor.fetchone()

    if not row:
        # Generate on-demand if candidate exists
        cursor.execute("""
        SELECT s.*, c.raw_text, c.file_type, j.required_skills, j.description AS jd_text
        FROM screenings s
        JOIN candidates c ON s.candidate_id = c.id
        JOIN jobs j ON s.job_id = j.id
        WHERE s.id = ?
        """, (screening_id,))
        cand_row = cursor.fetchone()
        if not cand_row:
            conn.close()
            raise HTTPException(status_code=404, detail="Screening record not found.")

        req_skills_raw = cand_row["required_skills"]
        try:
            req_skills = json.loads(req_skills_raw)
        except Exception:
            req_skills = [s.strip() for s in req_skills_raw.split(",") if s.strip()]

        eval_res = run_multi_agent_evaluation(
            resume_text=cand_row["raw_text"],
            required_skills=req_skills,
            jd_text=cand_row["jd_text"],
            file_type=cand_row["file_type"] or "pdf"
        )

        now = datetime.utcnow().isoformat()
        cursor.execute("""
        INSERT OR REPLACE INTO agent_evaluations (
            screening_id, security_report, entities_report, alignment_report,
            anomalies_report, interview_questions, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            screening_id,
            json.dumps(eval_res["security_defender"]),
            json.dumps(eval_res["entity_evidence"]),
            json.dumps(eval_res["deep_alignment"]),
            json.dumps(eval_res["anomaly_review"]),
            json.dumps(eval_res["interview_questions"]),
            now
        ))
        conn.commit()
        conn.close()

        return eval_res

    res = dict(row)
    conn.close()
    return {
        "security_defender": json.loads(res["security_report"]) if res.get("security_report") else {},
        "entity_evidence": json.loads(res["entities_report"]) if res.get("entities_report") else {},
        "deep_alignment": json.loads(res["alignment_report"]) if res.get("alignment_report") else {},
        "anomaly_review": json.loads(res["anomalies_report"]) if res.get("anomalies_report") else {},
        "interview_questions": json.loads(res["interview_questions"]) if res.get("interview_questions") else [],
        "evaluated_at": res.get("created_at")
    }

@router.post("/interview-questions/update")
def update_interview_questions(payload: UpdateInterviewQuestionsPayload):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE agent_evaluations 
    SET interview_questions = ? 
    WHERE screening_id = ?
    """, (json.dumps(payload.questions), payload.screening_id))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Interview questions updated successfully."}

# -------------------------------------------------------------------------
# 10. Recruiter Copilot (Natural-Language Structured + Semantic Search)
# -------------------------------------------------------------------------
@router.post("/copilot/search")
def search_copilot(payload: CopilotQueryPayload):
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Search query is required.")
    
    result = execute_copilot_search(
        query_text=payload.query.strip(),
        recruiter_id=payload.recruiter_id or "recruiter-default",
        custom_filters=payload.custom_filters
    )
    return result
