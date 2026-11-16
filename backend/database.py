"""
Database Layer for AI Resume Screening
======================================
Stores recruiters, jobs, candidates, screenings, and settings permanently in SQLite.
"""

import sqlite3
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

DB_DIR = Path(__file__).resolve().parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "screening.db"

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Recruiters table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recruiters (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        role TEXT DEFAULT 'Technical Recruiter',
        company TEXT DEFAULT 'Enterprise Talent Group',
        created_at TEXT NOT NULL
    )
    """)

    # Jobs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        recruiter_id TEXT NOT NULL,
        title TEXT NOT NULL,
        company TEXT DEFAULT 'Enterprise Talent Group',
        department TEXT DEFAULT 'Engineering',
        location TEXT DEFAULT 'San Francisco, CA / Remote',
        experience_required REAL DEFAULT 3.0,
        salary_range TEXT DEFAULT '$130,000 - $180,000',
        required_skills TEXT NOT NULL,
        nice_to_have_skills TEXT,
        description TEXT NOT NULL,
        status TEXT DEFAULT 'Active',
        created_at TEXT NOT NULL,
        FOREIGN KEY (recruiter_id) REFERENCES recruiters(id)
    )
    """)

    # Candidates table (with duplicate detection on recruiter_id + email)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id TEXT PRIMARY KEY,
        recruiter_id TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        skills TEXT,
        experience_years REAL DEFAULT 0.0,
        education TEXT,
        raw_text TEXT,
        original_filename TEXT,
        file_type TEXT,
        file_size INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY (recruiter_id) REFERENCES recruiters(id)
    )
    """)

    # Screenings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS screenings (
        id TEXT PRIMARY KEY,
        candidate_id TEXT NOT NULL,
        job_id TEXT NOT NULL,
        recruiter_id TEXT NOT NULL,
        score REAL NOT NULL,
        status TEXT NOT NULL,
        decision_reason TEXT NOT NULL,
        matched_skills TEXT,
        missing_skills TEXT,
        score_breakdown TEXT,
        model_predictions TEXT,
        manual_override INTEGER DEFAULT 0,
        override_by TEXT,
        override_reason TEXT,
        override_timestamp TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (candidate_id) REFERENCES candidates(id),
        FOREIGN KEY (job_id) REFERENCES jobs(id),
        FOREIGN KEY (recruiter_id) REFERENCES recruiters(id)
    )
    """)

    # Recruiter settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recruiter_settings (
        recruiter_id TEXT PRIMARY KEY,
        selected_threshold REAL DEFAULT 70.0,
        maybe_threshold REAL DEFAULT 50.0,
        blind_screening INTEGER DEFAULT 0,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (recruiter_id) REFERENCES recruiters(id)
    )
    """)

    conn.commit()

    # Seed default recruiter & initial jobs if not present
    seed_defaults(cursor, conn)
    conn.close()

def seed_defaults(cursor, conn):
    # Check if default recruiter exists
    cursor.execute("SELECT id FROM recruiters WHERE id = ?", ("recruiter-default",))
    if not cursor.fetchone():
        now = datetime.utcnow().isoformat()
        cursor.execute("""
        INSERT INTO recruiters (id, name, email, role, company, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "recruiter-default",
            "Jordan Davis",
            "recruiter@talentrank.ai",
            "Lead Technical Recruiter",
            "TalentRank Systems",
            now
        ))

        cursor.execute("""
        INSERT OR REPLACE INTO recruiter_settings (recruiter_id, selected_threshold, maybe_threshold, blind_screening, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """, ("recruiter-default", 70.0, 50.0, 0, now))

    # Seed default jobs for recruiter-default
    cursor.execute("SELECT count(*) as count FROM jobs WHERE recruiter_id = ?", ("recruiter-default",))
    count = cursor.fetchone()["count"]
    if count == 0:
        now = datetime.utcnow().isoformat()
        initial_jobs = [
            (
                "job-backend-senior",
                "recruiter-default",
                "Senior Backend Distributed Systems Engineer",
                "TalentRank Systems",
                "Platform Engineering",
                "San Francisco, CA / Remote",
                5.0,
                "$175,000 - $220,000",
                json.dumps(["Go", "Python", "Distributed Systems", "PostgreSQL", "Kafka", "Kubernetes"]),
                json.dumps(["gRPC", "Redis", "Docker", "AWS"]),
                "We are seeking an experienced Backend Engineer to scale our core streaming and distributed indexing services. Required expertise in Go or Python, microservices, Kafka event pipelines, and PostgreSQL optimization.",
                "Active",
                now
            ),
            (
                "job-ai-engineer",
                "recruiter-default",
                "Lead Machine Learning & NLP Engineer",
                "TalentRank Systems",
                "AI Research",
                "New York, NY / Remote",
                4.0,
                "$180,000 - $230,000",
                json.dumps(["Python", "PyTorch", "Transformers", "NLP", "Machine Learning", "FastAPI"]),
                json.dumps(["Vector Databases", "Docker", "Hugging Face", "MLOps"]),
                "Drive production deployment of deep learning sentence encoders, transformer models, and semantic search architectures. Hands-on PyTorch and NLP experience required.",
                "Active",
                now
            ),
            (
                "job-frontend-lead",
                "recruiter-default",
                "Staff Frontend UI/UX Architect",
                "TalentRank Systems",
                "Product Design",
                "Remote",
                4.0,
                "$160,000 - $205,000",
                json.dumps(["React", "TypeScript", "Tailwind CSS", "JavaScript", "HTML5", "UI/UX"]),
                json.dumps(["Next.js", "State Management", "Performance Optimization", "Figma"]),
                "Architect modern, responsive web dashboards and interactive generative data visualizations with high performance and accessibility standards.",
                "Active",
                now
            )
        ]
        cursor.executemany("""
        INSERT INTO jobs (id, recruiter_id, title, company, department, location, experience_required, salary_range, required_skills, nice_to_have_skills, description, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, initial_jobs)
        conn.commit()

# Initialize tables immediately on module load
init_db()
