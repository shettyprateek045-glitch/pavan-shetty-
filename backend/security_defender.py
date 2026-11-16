"""
Security & Prompt-Injection Defender
====================================
Core Rule: "RESUMES ARE DATA, NEVER ORDERS."

Treats all resume content strictly as passive untrusted data.
Scans for any text attempting to give orders, commands, or prompt overrides to the evaluator.
Any resume containing imperative orders/commands is flagged and marked as FRAUD.

Also uses PyMuPDF (fitz) to inspect:
1. White or near-background hidden text (color vs page background)
2. Microscopic / tiny text (< 4.0 pt)
3. Off-page / clipped text (bounding box outside visible page rectangle)
4. Invisible / zero-width / bidi unicode characters
5. Imperative command phrases and prompt-injection orders
"""

import re
import unicodedata
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

# Imperative order and manipulation patterns ("Resumes are data, never orders")
ORDER_AND_INJECTION_PATTERNS = [
    (r"\bignore\s+(?:all\s+)?(?:previous|prior|above|other)\s+instructions\b", "Command ordering system to ignore previous instructions"),
    (r"\bdisregard\s+(?:all\s+)?(?:prior|previous|above|other)\s+instructions\b", "Command ordering system to disregard instructions"),
    (r"\bforget\s+(?:all\s+)?(?:previous|prior)\s+instructions\b", "Command ordering system to forget instructions"),
    (r"\b(?:give|rank|score|rate)\s+(?:this\s+candidate|me|candidate)\s+(?:a\s+)?(?:100%?|perfect|top\s+score|maximum)\b", "Command ordering system to give 100% top score"),
    (r"\b(?:you\s+must|always|ensure\s+you)\s+(?:select|hire|shortlist|accept)\s+this\s+candidate\b", "Command ordering recruiter/AI to hire or select candidate"),
    (r"\bdo\s+not\s+(?:reject|fail|penalize|screen|filter)\s+(?:this\s+candidate|me)?\b", "Command ordering system not to reject or screen candidate"),
    (r"\b(?:set|force)\s+(?:status|score|rating)\s+to\s+(?:selected|100|top)\b", "Command ordering status/score override"),
    (r"\b(?:system\s+prompt|new\s+instruction|developer\s+mode|admin\s+override|jailbreak)\b", "Attempt to mimic system orders or administrative override"),
    (r"\bact\s+as\s+(?:an?\s+)?(?:unbiased\s+assistant\s+that\s+always\s+selects|evaluator\s+who\s+rates\s+me)\b", "Command instructing AI to act as compliant evaluator"),
    (r"\boutput\s*:\s*(?:selected|100%|hire)\b", "Command ordering output format forcing hire"),
    (r"\bimportant\s+instruction\s*:\s*", "Attempt to inject authoritative instructions into parser"),
    (r"\bprompt\s+injection\b", "Self-declared prompt injection keyword")
]

# Zero-width, invisible, and bidirectional override unicode characters
ZERO_WIDTH_CHARS = {
    '\u200B': 'Zero Width Space',
    '\u200C': 'Zero Width Non-Joiner',
    '\u200D': 'Zero Width Joiner',
    '\u200E': 'Left-to-Right Mark',
    '\u200F': 'Right-to-Left Mark',
    '\u202A': 'Left-to-Right Embedding',
    '\u202B': 'Right-to-Left Embedding',
    '\u202C': 'Pop Directional Formatting',
    '\u202D': 'Left-to-Right Override',
    '\u202E': 'Right-to-Left Override',
    '\uFEFF': 'Zero Width No-Break Space (Byte Order Mark)'
}

def analyze_pdf_security(file_bytes: bytes) -> Dict[str, Any]:
    """
    Performs comprehensive structural and span-level security analysis on a PDF using PyMuPDF.
    Flags any text giving orders/instructions and marks as FRAUD.
    """
    flags: List[Dict[str, Any]] = []
    checks_run = [
        "Hidden/white text detection (span color vs background)",
        "Microscopic/tiny font detection (< 4.0pt)",
        "Off-page / clipped text coordinates detection",
        "Zero-width and bidirectional unicode anomaly scan",
        "Resume-as-Data integrity scan (flagging any orders/commands as fraud)"
    ]
    checks_not_performed = [
        "Dynamic JavaScript execution analysis in PDF forms",
        "Embedded binary payload / shellcode disassembly",
        "Steganographic pixel-level image artifact inspection"
    ]

    try:
        import pymupdf as fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        return {
            "is_flagged": False,
            "is_fraud": False,
            "flags_count": 0,
            "flags": [],
            "checks_run": ["Basic binary readability check"],
            "checks_not_performed": checks_run + checks_not_performed,
            "hidden_text_detected": False,
            "prompt_injection_detected": False,
            "fraud_detected": False,
            "disclaimer": "Security scan fallback mode."
        }

    total_pages = len(doc)
    full_text = ""

    for page_idx in range(total_pages):
        page = doc[page_idx]
        page_rect = page.rect
        full_text += page.get_text() + "\n"

        page_dict = page.get_text("dict")
        blocks = page_dict.get("blocks", [])

        for b in blocks:
            if b.get("type") != 0:
                continue
            for line in b.get("lines", []):
                for span in line.get("spans", []):
                    span_text = span.get("text", "").strip()
                    if not span_text:
                        continue

                    font_size = span.get("size", 10.0)
                    font_color = span.get("color", 0)
                    bbox = span.get("bbox", (0, 0, 0, 0))

                    # 1. Microscopic / Tiny Text Check (< 3.8 pt)
                    if font_size < 3.8 and len(span_text) > 3:
                        flags.append({
                            "category": "Microscopic Text",
                            "severity": "Medium",
                            "is_fraud": False,
                            "reason": f"Extremely small text size ({round(font_size, 1)}pt) detected. Often used for keyword stuffing.",
                            "location": f"Page {page_idx + 1} at coordinates ({int(bbox[0])}, {int(bbox[1])})",
                            "flagged_text": span_text[:120],
                            "method_limitations": "Some legitimate copyright or header elements use small fonts."
                        })

                    # 2. White / Near-White Text Detection (against light background)
                    r = (font_color >> 16) & 255
                    g = (font_color >> 8) & 255
                    b_val = font_color & 255
                    if r > 242 and g > 242 and b_val > 242 and len(span_text) > 2:
                        flags.append({
                            "category": "Hidden / White Text",
                            "severity": "High",
                            "is_fraud": True,
                            "reason": f"Text rendered in near-white color (RGB {r},{g},{b_val}) on light background. Flagged as potential concealment fraud.",
                            "location": f"Page {page_idx + 1} at coordinates ({int(bbox[0])}, {int(bbox[1])})",
                            "flagged_text": span_text[:120],
                            "method_limitations": "Does not verify custom colored background boxes behind text."
                        })

                    # 3. Off-page / Clipped Text Detection
                    if (bbox[0] < -5 or bbox[1] < -5 or 
                        bbox[2] > page_rect.width + 10 or bbox[3] > page_rect.height + 10):
                        flags.append({
                            "category": "Off-Page Text",
                            "severity": "Medium",
                            "is_fraud": False,
                            "reason": "Text placed outside visible page crop rectangle.",
                            "location": f"Page {page_idx + 1} bounding box ({int(bbox[0])},{int(bbox[1])})",
                            "flagged_text": span_text[:100],
                            "method_limitations": "Bleed margins or export margins can position text outside standard boundaries."
                        })

    doc.close()

    # 4. Zero-Width Unicode Characters Scan
    for char, name in ZERO_WIDTH_CHARS.items():
        if char in full_text:
            count = full_text.count(char)
            flags.append({
                "category": "Hidden Unicode",
                "severity": "Medium",
                "is_fraud": False,
                "reason": f"Found {count} instance(s) of {name} (invisible character).",
                "location": "Document Text Body",
                "flagged_text": f"Character code: {repr(char)}",
                "method_limitations": "Some foreign language scripts legitimately employ non-joiners."
            })

    # 5. Imperative Orders & Prompt Injection Scan ("Resumes are data, never orders")
    fraud_orders_found = []
    for pattern, description in ORDER_AND_INJECTION_PATTERNS:
        matches = re.findall(pattern, full_text, flags=re.IGNORECASE)
        if matches:
            matched_phrase = matches[0] if isinstance(matches[0], str) else matches[0][0]
            fraud_orders_found.append(matched_phrase)
            flags.append({
                "category": "Fraud - Order Directive in Resume",
                "severity": "Critical",
                "is_fraud": True,
                "reason": f"RESUMES ARE DATA, NEVER ORDERS. Detected text giving orders/commands: {description}",
                "location": "Resume Body Text",
                "flagged_text": matched_phrase[:140],
                "method_limitations": "Strict pattern matching; candidate discussing prompt engineering in technical context should be verified by recruiter."
            })

    is_fraud = any(f.get("is_fraud", False) for f in flags)
    hidden_count = sum(1 for f in flags if "Hidden" in f["category"] or "Microscopic" in f["category"] or "Off-Page" in f["category"])
    injection_count = len(fraud_orders_found)

    return {
        "is_flagged": len(flags) > 0,
        "is_fraud": is_fraud,
        "fraud_detected": is_fraud,
        "fraud_reason": "FRAUD DETECTED: Resume text contained imperative orders/commands attempting to command the AI system. Resumes are data, never orders." if is_fraud else None,
        "flagged_orders": fraud_orders_found,
        "flags_count": len(flags),
        "flags": flags,
        "checks_run": checks_run,
        "checks_not_performed": checks_not_performed,
        "hidden_text_detected": hidden_count > 0,
        "prompt_injection_detected": injection_count > 0,
        "disclaimer": "Core Rule: Resumes are data, never orders. Any text giving instructions is flagged as potential fraud for human recruiter inspection."
    }

def analyze_raw_text_security(text: str) -> Dict[str, Any]:
    """
    Analyzes plaintext or docx text for zero-width characters and imperative orders.
    """
    flags: List[Dict[str, Any]] = []

    # 1. Zero-width Unicode
    for char, name in ZERO_WIDTH_CHARS.items():
        if char in text:
            count = text.count(char)
            flags.append({
                "category": "Hidden Unicode",
                "severity": "Medium",
                "is_fraud": False,
                "reason": f"Found {count} instance(s) of {name} (invisible character).",
                "location": "Text Stream",
                "flagged_text": f"Character code: {repr(char)}",
                "method_limitations": "Foreign language text may legitimately use non-joiners."
            })

    # 2. Imperative Orders & Prompt Injection Scan
    fraud_orders_found = []
    for pattern, description in ORDER_AND_INJECTION_PATTERNS:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches:
            matched_phrase = matches[0] if isinstance(matches[0], str) else matches[0][0]
            fraud_orders_found.append(matched_phrase)
            flags.append({
                "category": "Fraud - Order Directive in Resume",
                "severity": "Critical",
                "is_fraud": True,
                "reason": f"RESUMES ARE DATA, NEVER ORDERS. Detected text giving orders/commands: {description}",
                "location": "Text Body",
                "flagged_text": matched_phrase[:140],
                "method_limitations": "Mentions of prompt engineering should be verified by recruiter."
            })

    is_fraud = any(f.get("is_fraud", False) for f in flags)

    return {
        "is_flagged": len(flags) > 0,
        "is_fraud": is_fraud,
        "fraud_detected": is_fraud,
        "fraud_reason": "FRAUD DETECTED: Resume text contained imperative orders attempting to command the AI screening system. Resumes are data, never orders." if is_fraud else None,
        "flagged_orders": fraud_orders_found,
        "flags_count": len(flags),
        "flags": flags,
        "checks_run": [
            "Zero-width and bidirectional unicode anomaly scan",
            "Resume-as-Data integrity scan (flagging any orders/commands as fraud)"
        ],
        "checks_not_performed": [
            "Font-size span analysis (DOCX/TXT non-visual stream)",
            "Visual bounding box clipping check"
        ],
        "hidden_text_detected": False,
        "prompt_injection_detected": len(fraud_orders_found) > 0,
        "disclaimer": "Core Rule: Resumes are data, never orders. Any text giving instructions is flagged as potential fraud for human recruiter inspection."
    }

def sanitize_untrusted_resume_text(raw_text: str) -> str:
    """
    Wraps resume text in a strict data boundary to prevent prompt escape when feeding to downstream evaluators.
    """
    clean = re.sub(r'[\u200B-\u200F\u202A-\u202E\uFEFF]', '', raw_text)
    return f"""<RESUME_DATA_UNTRUSTED>
{clean}
</RESUME_DATA_UNTRUSTED>"""
