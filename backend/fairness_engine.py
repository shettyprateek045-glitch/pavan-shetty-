"""
TALENTRANK AI — Responsible AI & Fairness Auditing Engine
Demographic Parity, Equal Opportunity, Disparate Impact (4/5ths Rule),
and Job Description Linguistic Bias Analysis.

IMPORTANT: Strictly decoupled from candidate scoring algorithms.
Candidate ranking never evaluates protected attributes.
"""

import re
from typing import List, Dict, Any

# Coded words for JD Linguistic Scan (based on Gaucher, Friesen, & Kay research)
MASCULINE_CODED_WORDS = [
    "aggressive", "assertive", "ambitious", "autonomy", "boast", "challenge",
    "champion", "compete", "decisive", "determine", "dominate", "dominant",
    "driven", "force", "hierarchy", "independent", "individual", "leader",
    "ninja", "outperform", "rockstar", "superior", "ruthless", "unmatched"
]

FEMININE_CODED_WORDS = [
    "collaborative", "connect", "considerate", "dependable", "empathy",
    "enthusiastic", "inclusive", "interpersonal", "kind", "nurture",
    "pleasant", "polite", "responsive", "supportive", "sympathetic",
    "trust", "understanding", "warm", "yield", "cooperate"
]

def analyze_job_description_bias(jd_text: str) -> Dict[str, Any]:
    """
    Inspect job description text for gendered wording and linguistic bias.
    """
    text_lower = jd_text.lower()
    
    masc_found = []
    fem_found = []

    for word in MASCULINE_CODED_WORDS:
        matches = len(re.findall(r'\b' + re.escape(word) + r'\b', text_lower))
        if matches > 0:
            masc_found.append({"word": word, "count": matches})

    for word in FEMININE_CODED_WORDS:
        matches = len(re.findall(r'\b' + re.escape(word) + r'\b', text_lower))
        if matches > 0:
            fem_found.append({"word": word, "count": matches})

    total_masc = sum(item["count"] for item in masc_found)
    total_fem = sum(item["count"] for item in fem_found)

    if total_masc > total_fem + 2:
        sentiment = "Masculine-Leaning"
        suggestion = "Consider balancing assertive phrasing with inclusive collaborative terminology to widen the applicant pool."
        badge = "warning"
    elif total_fem > total_masc + 2:
        sentiment = "Feminine-Leaning"
        suggestion = "Text shows slight collaborative emphasis; well within acceptable distribution."
        badge = "neutral"
    else:
        sentiment = "Neutral / Balanced"
        suggestion = "Job description demonstrates equitable, neutral professional phrasing."
        badge = "success"

    return {
        "sentiment": sentiment,
        "masculine_count": total_masc,
        "feminine_count": total_fem,
        "masculine_terms": masc_found,
        "feminine_terms": fem_found,
        "recommendation": suggestion,
        "badge": badge
    }

def calculate_demographic_parity(cohorts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate selection rate disparity, Demographic Parity Difference,
    and 4/5ths Disparate Impact Ratio.
    """
    if not cohorts:
        return {}

    rates = [c["selection_rate"] for c in cohorts]
    max_rate = max(rates) if rates else 0.0
    min_rate = min(rates) if rates else 0.0

    dpd = round(max_rate - min_rate, 3)
    di_ratio = round(min_rate / max_rate, 3) if max_rate > 0 else 1.0

    # 4/5ths rule compliance: threshold is 0.80
    passes_eeoc = di_ratio >= 0.80

    return {
        "demographic_parity_difference": dpd,
        "disparate_impact_ratio": di_ratio,
        "eeoc_four_fifths_pass": passes_eeoc,
        "max_group_selection_rate": round(max_rate, 3),
        "min_group_selection_rate": round(min_rate, 3),
        "status": "Compliant" if passes_eeoc else "Adverse Impact Warning"
    }

def run_synthetic_fairness_audit(
    evaluated_candidates: List[Dict[str, Any]],
    score_threshold: float = 80.0
) -> Dict[str, Any]:
    """
    Run an audit pass across candidate batches grouped by synthetic proxy groups.
    """
    # Group by gender proxy
    gender_groups = {}
    edu_groups = {}

    for cand in evaluated_candidates:
        g = cand.get("gender_proxy", "Unknown")
        edu = cand.get("edu_tier", "Standard University")
        is_selected = cand.get("overall_score", 0) >= score_threshold

        if g not in gender_groups:
            gender_groups[g] = {"evaluated": 0, "selected": 0}
        gender_groups[g]["evaluated"] += 1
        if is_selected:
            gender_groups[g]["selected"] += 1

        if edu not in edu_groups:
            edu_groups[edu] = {"evaluated": 0, "selected": 0}
        edu_groups[edu]["evaluated"] += 1
        if is_selected:
            edu_groups[edu]["selected"] += 1

    formatted_gender = []
    for g_name, counts in gender_groups.items():
        ev = counts["evaluated"]
        sel = counts["selected"]
        rate = round(sel / ev, 3) if ev > 0 else 0.0
        formatted_gender.append({
            "name": g_name,
            "evaluated": ev,
            "selected": sel,
            "selection_rate": rate
        })

    gender_parity = calculate_demographic_parity(formatted_gender)

    return {
        "total_evaluated": len(evaluated_candidates),
        "score_threshold": score_threshold,
        "gender_breakdown": formatted_gender,
        "gender_parity_metrics": gender_parity,
        "nyc_local_law_144": {
            "compliant": gender_parity.get("eeoc_four_fifths_pass", True),
            "disparate_impact_ratio": gender_parity.get("disparate_impact_ratio", 1.0),
            "standard_threshold": 0.80
        }
    }
