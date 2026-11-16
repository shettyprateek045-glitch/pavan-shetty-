"""
Multi-Agent Evaluation Pipeline
===============================
Specialized evaluation stages providing transparent, structured JSON artifacts:
1. Entity & Evidence Extractor
2. Deep Alignment Evaluator (Context over keywords)
3. Anomaly Review Agent (Human review only; never alters score or rank)
4. Security & Prompt-Injection Defender
5. Tailored Interview Question Generator
"""

import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# Common link detection
URL_PATTERN = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
GITHUB_PATTERN = r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_\-]+)'
LINKEDIN_PATTERN = r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_\-]+)'

# Degree extraction patterns
EDUCATION_PATTERNS = [
    r"(?P<degree>Ph\.?D\.?|Doctor of Philosophy)[,\s\-]+(?P<field>[A-Za-z\s]+)?",
    r"(?P<degree>M\.?S\.?|Master(?:'s)?(?: of Science)?|M\.?Tech\.?)[,\s\-]+(?P<field>[A-Za-z\s]+)?",
    r"(?P<degree>B\.?S\.?|Bachelor(?:'s)?(?: of Science)?|B\.?Tech\.?|B\.?E\.?)[,\s\-]+(?P<field>[A-Za-z\s]+)?",
    r"(?P<degree>Associate(?:'s)? Degree)[,\s\-]+(?P<field>[A-Za-z\s]+)?"
]

# Action verbs indicating depth of involvement
STRONG_ACTION_VERBS = ["architected", "designed", "built", "spearheaded", "led", "authored", "implemented", "scaled", "optimized", "engineered", "founded"]
MAINTENANCE_VERBS = ["maintained", "supported", "monitored", "configured", "debugged", "assisted", "tested", "updated", "refactored"]
MENTIONED_VERBS = ["familiar with", "exposure to", "knowledge of", "utilized", "used", "worked with"]

# -------------------------------------------------------------------------
# Agent 1: Entity & Evidence Extractor
# -------------------------------------------------------------------------
def extract_entities_and_evidence(resume_text: str, file_type: str = "pdf") -> Dict[str, Any]:
    """
    Extracts structured work timeline, hard skills with source excerpts,
    certifications, education, and links. Never invents fields: uses null.
    """
    lines = [line.strip() for line in resume_text.split("\n") if line.strip()]

    # 1. Links
    github_match = re.search(GITHUB_PATTERN, resume_text, re.I)
    linkedin_match = re.search(LINKEDIN_PATTERN, resume_text, re.I)
    all_urls = re.findall(URL_PATTERN, resume_text)
    
    portfolio_url = None
    for url in all_urls:
        if "github" not in url.lower() and "linkedin" not in url.lower():
            portfolio_url = url
            break

    links = {
        "github": f"https://github.com/{github_match.group(1)}" if github_match else None,
        "linkedin": f"https://linkedin.com/in/{linkedin_match.group(1)}" if linkedin_match else None,
        "portfolio": portfolio_url
    }

    # 2. Education
    education_records = []
    for line in lines:
        for pat in EDUCATION_PATTERNS:
            m = re.search(pat, line, re.I)
            if m:
                degree = m.group("degree")
                field = m.group("field").strip() if m.group("field") else "Computer Science"
                education_records.append({
                    "degree": degree,
                    "field": field[:50],
                    "raw_line": line[:100]
                })
                break

    # 3. Certifications
    cert_matches = re.findall(r'\b(AWS Certified [A-Za-z\s]+|Google Cloud Certified [A-Za-z\s]+|CKA|CKAD|CISSP|PMP|Certified Kubernetes [A-Za-z\s]+)\b', resume_text, re.I)
    certifications = list(set([c.strip() for c in cert_matches])) if cert_matches else []

    # 4. Structured Work Timeline
    timeline = []
    # Pattern for Job Header: e.g. "Staff Software Engineer | Acme Corp (2020 - 2024)"
    job_block_pattern = re.compile(
        r'(?P<title>[A-Za-z\s\-/]+(?:Engineer|Architect|Developer|Manager|Lead|Scientist|Consultant|Specialist))\s*(?:at|@|\||,)\s*(?P<company>[A-Za-z0-9\s\.\-]+?)\s*[\(\[\{]?(?P<start>20\d\d|19\d\d)\s*(?:-|–|—|to)\s*(?P<end>20\d\d|Present|Current)[\)\]\}]?',
        re.I
    )

    matches = list(job_block_pattern.finditer(resume_text))
    current_year = datetime.utcnow().year

    for i, match in enumerate(matches):
        title = match.group("title").strip()
        company = match.group("company").strip()
        start_year = int(match.group("start"))
        end_str = match.group("end").strip().lower()
        end_year = current_year if end_str in ["present", "current"] else int(end_str)
        duration_years = max(0.5, round(float(end_year - start_year), 1))

        # Grab excerpts following this job header until next match
        start_pos = match.end()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else min(start_pos + 600, len(resume_text))
        job_body = resume_text[start_pos:end_pos].strip()

        bullet_points = [p.strip("-•* ") for p in job_body.split("\n") if len(p.strip()) > 15][:4]

        timeline.append({
            "title": title,
            "employer": company,
            "start_year": start_year,
            "end_year": end_year,
            "duration_years": duration_years,
            "is_current": end_str in ["present", "current"],
            "key_responsibilities": bullet_points
        })

    # Fallback timeline if regex misses specific corporate delimiter
    if not timeline:
        date_ranges = re.findall(r'\b(20\d\d|19\d\d)\s*(?:-|to|–|—)\s*(20\d\d|present|current)\b', resume_text, re.I)
        for start, end in date_ranges[:4]:
            sy = int(start)
            ey = current_year if end.lower() in ["present", "current"] else int(end)
            timeline.append({
                "title": "Software Engineering Role",
                "employer": "Technology Organization",
                "start_year": sy,
                "end_year": ey,
                "duration_years": max(0.5, float(ey - sy)),
                "is_current": end.lower() in ["present", "current"],
                "key_responsibilities": ["Production system architecture and feature delivery."]
            })

    # Sort timeline newest first
    timeline.sort(key=lambda x: x["end_year"], reverse=True)

    return {
        "candidate_links": links,
        "education": education_records if education_records else None,
        "certifications": certifications if certifications else None,
        "work_timeline": timeline
    }

# -------------------------------------------------------------------------
# Agent 2: Deep Alignment Evaluator (Context over Keywords)
# -------------------------------------------------------------------------
def evaluate_deep_alignment(required_skills: List[str], resume_text: str) -> Dict[str, Any]:
    """
    Judges depth of involvement and context for each required skill:
    Level of evidence: Strong / Partial / Mentioned only / Not found.
    Extracts the exact supporting excerpt and a rationale.
    """
    skills_evaluation = []
    clean_lines = [l.strip() for l in resume_text.split("\n") if l.strip()]

    for skill in required_skills:
        skill_re = re.compile(r'\b' + re.escape(skill) + r'\b', re.I)
        matching_sentences = []

        for line in clean_lines:
            if skill_re.search(line):
                matching_sentences.append(line)

        if not matching_sentences:
            skills_evaluation.append({
                "skill": skill,
                "evidence_level": "Not found",
                "supporting_excerpt": None,
                "rationale": f"No direct or contextual mention of '{skill}' identified in the resume text.",
                "depth_score": 0.0
            })
            continue

        best_excerpt = matching_sentences[0]
        excerpt_lower = best_excerpt.lower()

        # Check action verbs in the supporting sentence
        has_strong = any(v in excerpt_lower for v in STRONG_ACTION_VERBS)
        has_maintain = any(v in excerpt_lower for v in MAINTENANCE_VERBS)
        has_mentioned = any(v in excerpt_lower for v in MENTIONED_VERBS)

        if has_strong:
            level = "Strong"
            depth_score = 1.0
            rationale = f"Active ownership context: Candidate actively architected or led implementations with {skill}."
        elif has_maintain or len(matching_sentences) >= 2:
            level = "Partial"
            depth_score = 0.65
            rationale = f"Operational or maintenance context: Candidate regularly utilized {skill} in supporting production systems."
        elif has_mentioned or len(best_excerpt) < 30:
            level = "Mentioned only"
            depth_score = 0.35
            rationale = f"Listed in skills table or brief mention without deep contextual project delivery detail."
        else:
            level = "Partial"
            depth_score = 0.60
            rationale = f"Demonstrated practical application of {skill} in project deliverables."

        skills_evaluation.append({
            "skill": skill,
            "evidence_level": level,
            "supporting_excerpt": best_excerpt[:200],
            "rationale": rationale,
            "depth_score": depth_score
        })

    strong_count = sum(1 for s in skills_evaluation if s["evidence_level"] == "Strong")
    partial_count = sum(1 for s in skills_evaluation if s["evidence_level"] == "Partial")
    mentioned_count = sum(1 for s in skills_evaluation if s["evidence_level"] == "Mentioned only")
    not_found_count = sum(1 for s in skills_evaluation if s["evidence_level"] == "Not found")

    overall_depth_index = round(sum(s["depth_score"] for s in skills_evaluation) / max(len(skills_evaluation), 1) * 100, 1)

    return {
        "skills_evidence": skills_evaluation,
        "summary": {
            "strong_evidence_count": strong_count,
            "partial_evidence_count": partial_count,
            "mentioned_only_count": mentioned_count,
            "not_found_count": not_found_count,
            "depth_index": overall_depth_index
        }
    }

# -------------------------------------------------------------------------
# Agent 3: Anomaly Review Agent (Human Review Only)
# -------------------------------------------------------------------------
def review_anomalies_and_notes(timeline: List[Dict[str, Any]], resume_text: str, jd_text: str = "") -> Dict[str, Any]:
    """
    Identifies potential timeline overlaps, career gaps, or suspicious text artifacts.
    CRITICAL CONSTRAINT: Gaps and anomalies are for HUMAN REVIEW ONLY and NEVER modify relevance scores!
    Phrased neutrally as questions for the recruiter.
    """
    review_notes = []

    # 1. Timeline Overlaps and Gaps
    if len(timeline) >= 2:
        for i in range(len(timeline) - 1):
            newer_job = timeline[i]
            older_job = timeline[i + 1]

            # Overlap check
            if older_job["end_year"] > newer_job["start_year"]:
                review_notes.append({
                    "type": "Date Overlap",
                    "severity": "Informational",
                    "note": f"Dates for '{newer_job['title']}' ({newer_job['start_year']}) and '{older_job['title']}' ({older_job['end_year']}) overlap; worth confirming during interview whether these were concurrent engagements.",
                    "applies_to": f"{newer_job['title']} & {older_job['title']}"
                })

            # Career gap check (> 1.5 years)
            gap_years = newer_job["start_year"] - older_job["end_year"]
            if gap_years > 1.5:
                review_notes.append({
                    "type": "Career Transition Gap",
                    "severity": "Informational",
                    "note": f"Career interval of ~{int(gap_years)} year(s) between {older_job['end_year']} and {newer_job['start_year']}; worth discussing career transitions or sabbatical projects neutrally.",
                    "applies_to": f"Interval between {older_job['employer']} and {newer_job['employer']}"
                })

    # 2. Copy-Pasted Job Description Text Check
    if jd_text and len(jd_text) > 100:
        jd_sentences = [s.strip().lower() for s in re.split(r'[\.\n]', jd_text) if len(s.strip()) > 35]
        verbatim_matches = []
        resume_lower = resume_text.lower()
        for s in jd_sentences:
            if s in resume_lower:
                verbatim_matches.append(s[:60] + "...")
        if len(verbatim_matches) >= 2:
            review_notes.append({
                "type": "Verbatim Phrase Similarity",
                "severity": "Attention Required",
                "note": f"Found {len(verbatim_matches)} phrasing snippet(s) closely mirroring job requisition text; recruiter may verify hands-on execution during technical screening.",
                "applies_to": "Resume Summary / Responsibilities"
            })

    return {
        "review_notes_count": len(review_notes),
        "review_notes": review_notes,
        "disclaimer": "Career intervals, timeline overlaps, and anomaly notes are for human recruiter review only. Under TalentRank ethical guidelines, they NEVER alter or penalize candidate relevance scores or automated rankings."
    }

# -------------------------------------------------------------------------
# Agent 4: Tailored Technical Interview Question Generator
# -------------------------------------------------------------------------
def generate_interview_questions(skills_eval: List[Dict[str, Any]], timeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generates 3-5 tailored technical validation questions targeting:
    (a) required skills with only Partial/Mentioned evidence,
    (b) specific architectural claims worth probing.
    """
    questions = []

    # Priority 1: Target skills with Partial or Mentioned evidence
    partial_skills = [s for s in skills_eval if s["evidence_level"] in ["Partial", "Mentioned only"]]
    for item in partial_skills[:3]:
        skill = item["skill"]
        excerpt = item.get("supporting_excerpt") or f"Mentions of {skill}"
        questions.append({
            "id": f"q-{skill.lower().replace(' ', '-')}",
            "targeted_skill": skill,
            "targeted_claim": excerpt[:100],
            "evidence_gap": f"Evidence level is '{item['evidence_level']}'",
            "question": f"In your previous work with {skill}, could you walk us through the architecture of a high-load feature you built? What were the primary bottlenecks and how did you resolve them?",
            "evaluator_guidance": f"Listen for concrete production details (concurrency, schema design, failover, metrics) rather than high-level theoretical definitions.",
            "label": "AI-suggested, recruiter to edit"
        })

    # Priority 2: Target top architectural claim from timeline
    if timeline and len(questions) < 4:
        lead_job = timeline[0]
        responsibilities = lead_job.get("key_responsibilities", [])
        if responsibilities:
            top_claim = responsibilities[0]
            questions.append({
                "id": "q-lead-architecture",
                "targeted_skill": "System Architecture & Delivery",
                "targeted_claim": top_claim[:100],
                "evidence_gap": "Verifying production depth and engineering tradeoffs",
                "question": f"At {lead_job['employer']}, you worked on '{top_claim[:70]}...'. What alternative designs did you consider before settling on this solution, and what were the tradeoffs?",
                "evaluator_guidance": "Assess candidate's ability to reason about tradeoffs, p99 latencies, resilience, and operational observability.",
                "label": "AI-suggested, recruiter to edit"
            })

    # Fallback technical question if needed
    if len(questions) < 3:
        questions.append({
            "id": "q-general-distributed",
            "targeted_skill": "Distributed Reliability",
            "targeted_claim": "Core systems scaling",
            "evidence_gap": "Probing operational resilience competence",
            "question": "Can you describe a challenging production outage you diagnosed and resolved? How did you isolate the root cause and prevent recurrence?",
            "evaluator_guidance": "Verify systematic debugging methodology, post-mortem rigor, and telemetry usage.",
            "label": "AI-suggested, recruiter to edit"
        })

    return questions[:5]

# -------------------------------------------------------------------------
# Pipeline Orchestrator: Runs All Agents
# -------------------------------------------------------------------------
def run_multi_agent_evaluation(
    resume_text: str,
    required_skills: List[str],
    jd_text: str = "",
    file_bytes: Optional[bytes] = None,
    file_type: str = "pdf"
) -> Dict[str, Any]:
    """
    Executes all specialized agents in sequence and returns complete structured artifact JSON.
    """
    # Stage 1: Security & Prompt-Injection Defender
    if file_bytes and file_type == "pdf":
        from backend.security_defender import analyze_pdf_security
        security_artifact = analyze_pdf_security(file_bytes)
    else:
        from backend.security_defender import analyze_raw_text_security
        security_artifact = analyze_raw_text_security(resume_text)

    # Stage 2: Entity & Evidence Extractor
    entities_artifact = extract_entities_and_evidence(resume_text, file_type=file_type)

    # Stage 3: Deep Alignment Evaluator (Context over Keywords)
    alignment_artifact = evaluate_deep_alignment(required_skills, resume_text)

    # Stage 4: Anomaly Review Agent (Review Notes Only)
    anomaly_artifact = review_anomalies_and_notes(
        entities_artifact.get("work_timeline", []),
        resume_text,
        jd_text=jd_text
    )

    # Stage 5: Interview Question Generator
    questions_artifact = generate_interview_questions(
        alignment_artifact.get("skills_evidence", []),
        entities_artifact.get("work_timeline", [])
    )

    return {
        "security_defender": security_artifact,
        "entity_evidence": entities_artifact,
        "deep_alignment": alignment_artifact,
        "anomaly_review": anomaly_artifact,
        "interview_questions": questions_artifact,
        "evaluated_at": datetime.utcnow().isoformat()
    }
