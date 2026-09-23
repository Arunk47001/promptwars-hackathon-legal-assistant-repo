"""PII masking module (C6).

Regex-based Aadhaar/PAN detection and redaction, applied only at the point
content is written to persistent storage or application logs.

IMPORTANT (documented, accepted POC-level limitation — per the plan's
"Decisions resolved #8"): this masking is explicitly NOT applied before the
outbound Gemini call. The ingestion pipeline (C7) sends the raw document
image/PDF/text to Gemini for native multimodal extraction and reasoning
*before* this module ever runs. Masking here only protects what Namma Nyaya
itself persists to disk/DB or writes to logs — raw content (including any
embedded Aadhaar/PAN numbers) still reaches Google's Gemini API in-flight.
A production version would need masking (or reviewed data-handling terms)
before any external LLM call too.
"""
from __future__ import annotations

import re

# Aadhaar: 12 digits, commonly formatted as 4-4-4 with spaces or hyphens.
AADHAAR_PATTERN = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")

# PAN: 5 letters, 4 digits, 1 letter (standard Indian PAN format).
PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")

AADHAAR_MASK = "[REDACTED-AADHAAR]"
PAN_MASK = "[REDACTED-PAN]"


def mask_pii(text: str) -> str:
    """Return a copy of `text` with Aadhaar- and PAN-shaped substrings
    redacted. Order matters: PAN (letters+digits+letter) is checked first
    since it cannot collide with the pure-digit Aadhaar pattern, so either
    order is actually safe, but PAN first keeps intent obvious."""
    if not text:
        return text
    masked = PAN_PATTERN.sub(PAN_MASK, text)
    masked = AADHAAR_PATTERN.sub(AADHAAR_MASK, masked)
    return masked


def contains_pii(text: str) -> bool:
    return bool(AADHAAR_PATTERN.search(text) or PAN_PATTERN.search(text))
