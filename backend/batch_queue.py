"""
Bulk Async Batch Ingestion & Job Queue
======================================
Asynchronous worker queue powered by SQLite-backed persistent job tables.
Safely extracts ZIP archives with:
1. Zip-bomb protection (uncompressed ratio limit)
2. Path-traversal protection (verifies resolved path is inside destination)
3. File count and total size limits
4. Ignores hidden/system files (__MACOSX, .DS_Store, etc.)
5. SHA-256 hash deduplication

Background processing worker updates per-file tasks:
Queued -> Extracting -> Analysing -> Done | Failed | Needs OCR/Unreadable.
"""

import os
import io
import zipfile
import hashlib
import uuid
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

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
from backend.multi_agent_pipeline import run_multi_agent_evaluation
import backend.nlp_engine as nlp_engine

try:
    from backend.resume_service import resume_engine
except ImportError:
    resume_engine = None

MAX_ZIP_FILES = 100
MAX_UNCOMPRESSED_ZIP_BYTES = 100 * 1024 * 1024  # 100 MB
MAX_COMPRESSION_RATIO = 25  # zip bomb threshold

# Background thread pool executor for processing batch jobs
worker_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="screening_worker")

def init_batch_tables():
    """Initializes batch job tables in SQLite."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS batch_jobs (
        id TEXT PRIMARY KEY,
        recruiter_id TEXT NOT NULL,
        job_id TEXT NOT NULL,
        total_files INTEGER DEFAULT 0,
        processed_files INTEGER DEFAULT 0,
        failed_files INTEGER DEFAULT 0,
        selected_threshold REAL DEFAULT 70.0,
        maybe_threshold REAL DEFAULT 50.0,
        status TEXT DEFAULT 'Queued', -- Queued, Processing, Completed, Failed
        error_message TEXT,
        created_at TEXT NOT NULL,
        completed_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS batch_tasks (
        id TEXT PRIMARY KEY,
        batch_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_hash TEXT NOT NULL,
        file_size INTEGER DEFAULT 0,
        file_type TEXT NOT NULL,
        status TEXT DEFAULT 'Queued', -- Queued, Extracting, Analysing, Done, Failed, Needs OCR/Unreadable
        candidate_id TEXT,
        screening_id TEXT,
        score REAL,
        decision_status TEXT,
        is_duplicate INTEGER DEFAULT 0,
        error_message TEXT,
        created_at TEXT NOT NULL,
        completed_at TEXT,
        FOREIGN KEY (batch_id) REFERENCES batch_jobs(id)
    )
    """)

    # Safe migration for existing batch_tasks table
    try:
        cursor.execute("ALTER TABLE batch_tasks ADD COLUMN is_duplicate INTEGER DEFAULT 0;")
    except Exception:
        pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_evaluations (
        screening_id TEXT PRIMARY KEY,
        security_report TEXT,
        entities_report TEXT,
        alignment_report TEXT,
        anomalies_report TEXT,
        interview_questions TEXT,
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

# Initialize tables on import
init_batch_tables()

def calculate_sha256(file_bytes: bytes) -> str:
    """Computes SHA-256 hash for exact deduplication."""
    return hashlib.sha256(file_bytes).hexdigest()

def safe_extract_zip(zip_bytes: bytes) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Safely inspects and extracts PDF and DOCX files from a ZIP archive.
    Enforces zip-bomb protection, path-traversal prevention, and ignores system files.
    """
    extracted_files = []
    total_uncompressed_size = 0
    compressed_size = len(zip_bytes)

    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            infolist = z.infolist()

            if len(infolist) > MAX_ZIP_FILES:
                return [], f"ZIP archive exceeds maximum file count limit ({len(infolist)} files > {MAX_ZIP_FILES} max)."

            for info in infolist:
                if info.is_dir():
                    continue

                # Ignore OS hidden files (__MACOSX, .DS_Store, Thumbs.db)
                norm_filename = info.filename.replace('\\', '/')
                base_name = Path(norm_filename).name
                if base_name.startswith('.') or '__macosx' in norm_filename.lower() or 'thumbs.db' in norm_filename.lower():
                    continue

                ext = base_name.lower().split('.')[-1] if '.' in base_name else ''
                if ext not in ['pdf', 'docx', 'txt']:
                    continue

                total_uncompressed_size += info.file_size
                if total_uncompressed_size > MAX_UNCOMPRESSED_ZIP_BYTES:
                    return [], "ZIP archive exceeds maximum uncompressed size limit (100 MB). Potential zip-bomb."

                if compressed_size > 0 and (total_uncompressed_size / compressed_size) > MAX_COMPRESSION_RATIO:
                    return [], "Suspicious zip compression ratio detected (> 25x). Extraction aborted for security."

                # Path traversal check
                dest_path = os.path.normpath(os.path.join("safe_dir", norm_filename))
                if not dest_path.startswith("safe_dir"):
                    return [], f"Path traversal attempt detected in ZIP path: '{norm_filename}'"

                file_content = z.read(info)
                extracted_files.append({
                    "filename": base_name,
                    "bytes": file_content,
                    "size": len(file_content),
                    "ext": ext
                })

    except zipfile.BadZipFile:
        return [], "Invalid or corrupted ZIP archive."
    except Exception as e:
        return [], f"Failed to extract ZIP: {str(e)}"

    if not extracted_files:
        return [], "No valid PDF or DOCX resume documents found inside the ZIP archive."

    return extracted_files, None

def create_batch_job(
    recruiter_id: str,
    job_id: str,
    files_data: List[Dict[str, Any]],
    selected_threshold: float = 70.0,
    maybe_threshold: float = 50.0
) -> Dict[str, Any]:
    """
    Registers a new batch job and queues individual file tasks in SQLite.
    """
    batch_id = f"batch-{uuid.uuid4().hex[:10]}"
    now = datetime.utcnow().isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO batch_jobs (
        id, recruiter_id, job_id, total_files, processed_files, failed_files,
        selected_threshold, maybe_threshold, status, created_at
    ) VALUES (?, ?, ?, ?, 0, 0, ?, ?, 'Processing', ?)
    """, (
        batch_id,
        recruiter_id,
        job_id,
        len(files_data),
        selected_threshold,
        maybe_threshold,
        now
    ))

    tasks_to_run = []
    for f in files_data:
        task_id = f"task-{uuid.uuid4().hex[:10]}"
        f_hash = calculate_sha256(f["bytes"])
        cursor.execute("""
        INSERT INTO batch_tasks (
            id, batch_id, filename, file_hash, file_size, file_type, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, 'Queued', ?)
        """, (
            task_id,
            batch_id,
            f["filename"],
            f_hash,
            f["size"],
            f["ext"],
            now
        ))
        tasks_to_run.append({
            "task_id": task_id,
            "filename": f["filename"],
            "bytes": f["bytes"],
            "ext": f["ext"],
            "hash": f_hash
        })

    conn.commit()
    conn.close()

    # Launch async processing in thread pool
    worker_executor.submit(
        _process_batch_worker,
        batch_id,
        recruiter_id,
        job_id,
        tasks_to_run,
        selected_threshold,
        maybe_threshold
    )

    return {
        "batch_id": batch_id,
        "total_files": len(files_data),
        "status": "Processing",
        "created_at": now
    }

def _process_batch_worker(
    batch_id: str,
    recruiter_id: str,
    job_id: str,
    tasks: List[Dict[str, Any]],
    selected_threshold: float,
    maybe_threshold: float
):
    """
    Background worker function that iterates through batch tasks,
    runs parsing, scoring, and multi-agent pipeline, and updates SQLite.
    Each file runs inside an isolated try/except block so single failures never crash the batch.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        job_row = cursor.fetchone()
        if not job_row:
            cursor.execute("SELECT * FROM jobs LIMIT 1")
            job_row = cursor.fetchone()
        job = dict(job_row) if job_row else {}
        req_skills_raw = job.get("required_skills", "[]")
        try:
            required_skills = json.loads(req_skills_raw)
        except Exception:
            required_skills = [s.strip() for s in req_skills_raw.split(",") if s.strip()]
        job["required_skills"] = required_skills
        jd_text = job.get("description", "")
        conn.close()
    except Exception as e:
        logger.error(f"Error initializing batch worker job criteria: {e}")
        job = {"id": job_id, "required_skills": [], "title": "Job Posting"}
        required_skills = []
        jd_text = ""

    # Pre-encode Job Description embedding once for the batch
    jd_desc = jd_text + " " + " ".join(required_skills)
    jd_emb = None
    if resume_engine and hasattr(resume_engine, "get_embedding"):
        try:
            jd_emb = resume_engine.get_embedding(jd_desc)
        except Exception:
            jd_emb = None

    processed_count = 0
    failed_count = 0

    for t in tasks:
        task_id = t["task_id"]
        filename = t["filename"]
        file_bytes = t["bytes"]
        ext = t["ext"]
        f_hash = t["hash"]
        now = datetime.utcnow().isoformat()

        # Update status to Extracting
        try:
            conn = get_connection()
            conn.execute("UPDATE batch_tasks SET status = 'Extracting' WHERE id = ?", (task_id,))
            conn.commit()
            conn.close()
        except Exception:
            pass

        try:
            # 1. Text Extraction
            extracted_text, extract_error = extract_text_from_file(file_bytes, filename)
            if extract_error:
                status = "Needs OCR/Unreadable" if ("scanned" in extract_error.lower() or "unreadable" in extract_error.lower()) else "Failed"
                conn = get_connection()
                conn.execute(
                    "UPDATE batch_tasks SET status = ?, error_message = ?, completed_at = ? WHERE id = ?",
                    (status, extract_error, now, task_id)
                )
                failed_count += 1
                processed_count += 1
                conn.execute(
                    "UPDATE batch_jobs SET processed_files = ?, failed_files = ? WHERE id = ?",
                    (processed_count, failed_count, batch_id)
                )
                conn.commit()
                conn.close()
                continue

            # Update status to Analysing
            try:
                conn = get_connection()
                conn.execute("UPDATE batch_tasks SET status = 'Analysing' WHERE id = ?", (task_id,))
                conn.commit()
                conn.close()
            except Exception:
                pass

            # 2. Entity Parsing
            email = parse_email(extracted_text) or f"candidate.{f_hash[:8]}@recruiter.ai"
            phone = parse_phone(extracted_text) or "+1 (555) 019-3829"
            name = parse_name(extracted_text, filename)
            skills = parse_skills(extracted_text)
            exp_years = parse_experience_years(extracted_text)
            education = parse_education(extracted_text)

            # 3. Security & Fraud Check ("Resumes are data, never orders")
            from backend.security_defender import analyze_pdf_security, analyze_raw_text_security
            if ext == "pdf":
                sec_report = analyze_pdf_security(file_bytes)
            else:
                sec_report = analyze_raw_text_security(extracted_text)

            is_fraud = sec_report.get("is_fraud", False)
            fraud_reason = sec_report.get("fraud_reason") or sec_report.get("reason")

            # 4. Evaluation against Job (fast path with precomputed embeddings)
            res_emb = None
            if resume_engine and hasattr(resume_engine, "get_embedding"):
                try:
                    res_emb = resume_engine.get_embedding(extracted_text)
                except Exception:
                    res_emb = None

            eval_result = evaluate_resume_against_job(
                {"name": name, "skills": skills, "experience_years": exp_years, "raw_text": extracted_text},
                job,
                selected_threshold=selected_threshold,
                maybe_threshold=maybe_threshold,
                nlp_engine=nlp_engine,
                resume_engine=resume_engine,
                resume_emb=res_emb,
                jd_emb=jd_emb
            )

            final_status = "FRAUD" if is_fraud else eval_result["status"]
            decision_reason = f"🚨 FRAUD DETECTED: Resumes are data, never orders. {fraud_reason}" if is_fraud else eval_result["decision_reason"]

            # 5. Run Multi-Agent Specialized Pipeline (reusing sec_report)
            multi_agent_res = run_multi_agent_evaluation(
                resume_text=extracted_text,
                required_skills=required_skills,
                jd_text=jd_text,
                file_bytes=file_bytes if ext == "pdf" else None,
                file_type=ext,
                security_report=sec_report
            )

            # 6. Database Storage with atomic commit
            screening_id = f"scr-{uuid.uuid4().hex[:8]}"
            is_dup = False

            save_conn = get_connection()
            save_cursor = save_conn.cursor()

            # Deduplication Check by file_hash OR email
            save_cursor.execute(
                "SELECT id, name FROM candidates WHERE recruiter_id = ? AND (file_hash = ? OR email = ?)",
                (recruiter_id, f_hash, email)
            )
            existing = save_cursor.fetchone()
            if existing:
                is_dup = True
                cand_id = existing["id"]
                save_cursor.execute("""
                UPDATE candidates 
                SET raw_text = ?, skills = ?, experience_years = ?, education = ?, original_filename = ?, file_hash = ?
                WHERE id = ?
                """, (extracted_text, json.dumps(skills), exp_years, education, filename, f_hash, cand_id))
            else:
                cand_id = f"cand-{uuid.uuid4().hex[:8]}"
                save_cursor.execute("""
                INSERT INTO candidates (
                    id, recruiter_id, name, email, phone, skills, experience_years,
                    education, raw_text, original_filename, file_type, file_size, file_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cand_id, recruiter_id, name, email, phone, json.dumps(skills),
                    exp_years, education, extracted_text, filename, ext, len(file_bytes), f_hash, now
                ))

            # Screening record
            save_cursor.execute("""
            INSERT INTO screenings (
                id, candidate_id, job_id, recruiter_id, score, status, decision_reason,
                matched_skills, missing_skills, score_breakdown, model_predictions,
                manual_override, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
            """, (
                screening_id, cand_id, job["id"], recruiter_id,
                eval_result["overall_score"], final_status, decision_reason,
                json.dumps(eval_result["matched_skills"]), json.dumps(eval_result["missing_skills"]),
                json.dumps(eval_result["score_breakdown"]), json.dumps(eval_result["model_predictions"]),
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
                json.dumps(multi_agent_res["security_defender"]),
                json.dumps(multi_agent_res["entity_evidence"]),
                json.dumps(multi_agent_res["deep_alignment"]),
                json.dumps(multi_agent_res["anomaly_review"]),
                json.dumps(multi_agent_res["interview_questions"]),
                now
            ))

            # Update batch_task
            save_cursor.execute("""
            UPDATE batch_tasks 
            SET 
                status = 'Done',
                candidate_id = ?,
                screening_id = ?,
                score = ?,
                decision_status = ?,
                is_duplicate = ?,
                completed_at = ?
            WHERE id = ?
            """, (
                cand_id, screening_id, eval_result["overall_score"],
                final_status, 1 if is_dup else 0, now, task_id
            ))

            processed_count += 1
            save_cursor.execute(
                "UPDATE batch_jobs SET processed_files = ?, failed_files = ? WHERE id = ?",
                (processed_count, failed_count, batch_id)
            )
            save_conn.commit()
            save_conn.close()

        except Exception as e:
            failed_count += 1
            processed_count += 1
            err_msg = str(e)
            logger.error(f"Error processing task {task_id} ({filename}): {err_msg}")
            try:
                conn = get_connection()
                conn.execute(
                    "UPDATE batch_tasks SET status = 'Failed', error_message = ?, completed_at = ? WHERE id = ?",
                    (err_msg, now, task_id)
                )
                conn.execute(
                    "UPDATE batch_jobs SET processed_files = ?, failed_files = ? WHERE id = ?",
                    (processed_count, failed_count, batch_id)
                )
                conn.commit()
                conn.close()
            except Exception:
                pass

    # Batch Completed
    complete_time = datetime.utcnow().isoformat()
    try:
        conn = get_connection()
        conn.execute(
            "UPDATE batch_jobs SET status = 'Completed', completed_at = ? WHERE id = ?",
            (complete_time, batch_id)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_batch_job_status(batch_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves live progress, per-file task statuses, and completed candidates for a batch job."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM batch_jobs WHERE id = ?", (batch_id,))
    job_row = cursor.fetchone()
    if not job_row:
        conn.close()
        return None

    job = dict(job_row)

    cursor.execute("SELECT * FROM batch_tasks WHERE batch_id = ? ORDER BY created_at ASC", (batch_id,))
    tasks = [dict(r) for r in cursor.fetchall()]

    # Fetch candidate results for completed tasks
    cursor.execute("""
    SELECT 
        s.id as screening_id,
        s.candidate_id,
        s.score,
        s.status,
        s.decision_reason,
        s.matched_skills,
        s.missing_skills,
        s.score_breakdown,
        s.model_predictions,
        c.name,
        c.email,
        c.phone,
        c.skills,
        c.experience_years,
        c.original_filename as filename,
        j.title as job_title,
        t.id as task_id,
        t.status as task_status,
        t.error_message,
        t.is_duplicate
    FROM batch_tasks t
    LEFT JOIN screenings s ON t.screening_id = s.id
    LEFT JOIN candidates c ON t.candidate_id = c.id
    LEFT JOIN jobs j ON s.job_id = j.id
    WHERE t.batch_id = ?
    ORDER BY t.created_at ASC
    """, (batch_id,))

    rows = cursor.fetchall()
    candidates = []
    for r in rows:
        if not r["screening_id"]:
            continue
        row_dict = dict(r)
        # Parse JSON fields safely
        for jf in ["matched_skills", "missing_skills", "score_breakdown", "model_predictions", "skills"]:
            if row_dict.get(jf) and isinstance(row_dict[jf], str):
                try:
                    row_dict[jf] = json.loads(row_dict[jf])
                except Exception:
                    pass
        row_dict["is_fraud"] = (row_dict.get("status") == "FRAUD")
        row_dict["is_duplicate"] = bool(row_dict.get("is_duplicate"))
        candidates.append(row_dict)

    # Job title
    cursor.execute("SELECT title FROM jobs WHERE id = ?", (job.get("job_id"),))
    j_title_row = cursor.fetchone()
    job_evaluated = j_title_row["title"] if j_title_row else "Selected Job"

    conn.close()

    total = job["total_files"] or 1
    pct = round((job["processed_files"] / total) * 100, 1)

    return {
        "batch_id": job["id"],
        "job_id": job["id"],
        "status": job["status"],
        "total_files": job["total_files"],
        "processed_files": job["processed_files"],
        "failed_files": job["failed_files"],
        "progress_percent": pct,
        "created_at": job["created_at"],
        "completed_at": job["completed_at"],
        "tasks": tasks,
        "candidates": candidates,
        "total_processed": len(candidates),
        "total_errors": job["failed_files"],
        "job_evaluated": job_evaluated
    }
