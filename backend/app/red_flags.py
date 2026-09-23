"""Red-flag detection engine (C11).

Rules+retrieval hybrid against the curated source set (C9), covering the
spec's MVP red-flag list verbatim:
    - deposit size norms
    - painting/cleaning deduction clauses
    - lock-in asymmetry
    - non-compete enforceability (Contract Act Section 27)
    - training bond enforceability

Implementation is deterministic regex/keyword rules over the extracted
document text (not a free-form Gemini call), so results are reproducible and
testable without a live key, and every flag's citation is a real id from
app.legal_sources.CURATED_SOURCES (no fabricated citations). This matches
the task breakdown's own framing of C11 as a "rules+retrieval hybrid," and
sidesteps the risk of an LLM inventing a plausible-sounding but wrong
citation.
"""
from __future__ import annotations

import re

from app.legal_sources import get_source
from app.models import RedFlag

_DEPOSIT_MONTHS_RE = re.compile(
    r"(?:security\s+deposit[^.\n]{0,40}?|deposit\s+of\s+)(\d+)\s*(?:months?|month's)",
    re.IGNORECASE,
)
_LOCK_IN_RE = re.compile(r"lock[- ]?in", re.IGNORECASE)
_TENANT_NOTICE_RE = re.compile(
    r"tenant[^.\n]{0,60}?(\d+)\s*months?\s*notice", re.IGNORECASE
)
_LANDLORD_NOTICE_RE = re.compile(
    r"landlord[^.\n]{0,60}?(\d+)\s*months?\s*notice", re.IGNORECASE
)
_PAINTING_RE = re.compile(r"painting|cleaning\s+charges?", re.IGNORECASE)
_REGARDLESS_RE = re.compile(r"regardless of|irrespective of|shall be deducted", re.IGNORECASE)
_NON_COMPETE_RE = re.compile(r"non[- ]?compete|restraint of trade", re.IGNORECASE)
_TRAINING_BOND_RE = re.compile(r"training bond|bond amount|service bond", re.IGNORECASE)


def _excerpt(text: str, match: re.Match, pad: int = 60) -> str:
    start = max(0, match.start() - pad)
    end = min(len(text), match.end() + pad)
    return text[start:end].strip().replace("\n", " ")


def detect_red_flags(text: str) -> list[RedFlag]:
    flags: list[RedFlag] = []

    # 1. Deposit size norms
    for m in _DEPOSIT_MONTHS_RE.finditer(text):
        months = int(m.group(1))
        if months > 4:
            src = get_source("karnataka-rent-act-deposit")
            flags.append(
                RedFlag(
                    category="deposit_size",
                    severity="high" if months >= 8 else "medium",
                    clause_excerpt=_excerpt(text, m),
                    explanation=(
                        f"A security deposit of {months} months' rent is well above "
                        "the customary 2-3 month range for Bengaluru residential "
                        "tenancies and is worth negotiating."
                    ),
                    citation=f"{src.statute}, {src.section}" if src else "",
                )
            )

    # 2. Painting/cleaning deduction clauses
    for m in _PAINTING_RE.finditer(text):
        window = text[max(0, m.start() - 80) : m.end() + 80]
        if _REGARDLESS_RE.search(window):
            src = get_source("karnataka-rent-act-deductions")
            flags.append(
                RedFlag(
                    category="painting_cleaning_deduction",
                    severity="medium",
                    clause_excerpt=_excerpt(text, m),
                    explanation=(
                        "This clause deducts painting/cleaning charges regardless "
                        "of the property's actual condition at handover, which is "
                        "a commonly flagged unfair-deduction pattern."
                    ),
                    citation=f"{src.statute}, {src.section}" if src else "",
                )
            )

    # 3. Lock-in asymmetry (tenant notice much longer than landlord's)
    tenant_match = _TENANT_NOTICE_RE.search(text)
    landlord_match = _LANDLORD_NOTICE_RE.search(text)
    if tenant_match and landlord_match:
        tenant_months = int(tenant_match.group(1))
        landlord_months = int(landlord_match.group(1))
        if tenant_months > landlord_months:
            src = get_source("karnataka-rent-act-notice")
            flags.append(
                RedFlag(
                    category="lock_in_asymmetry",
                    severity="medium",
                    clause_excerpt=_excerpt(text, tenant_match),
                    explanation=(
                        f"The tenant must give {tenant_months} months' notice while "
                        f"the landlord only needs to give {landlord_months} month(s) "
                        "— this asymmetry disproportionately burdens the tenant."
                    ),
                    citation=f"{src.statute}, {src.section}" if src else "",
                )
            )
    elif _LOCK_IN_RE.search(text):
        src = get_source("karnataka-rent-act-notice")
        m = _LOCK_IN_RE.search(text)
        flags.append(
            RedFlag(
                category="lock_in_asymmetry",
                severity="low",
                clause_excerpt=_excerpt(text, m),
                explanation=(
                    "A lock-in clause is present; verify both parties face "
                    "comparably fair exit terms."
                ),
                citation=f"{src.statute}, {src.section}" if src else "",
            )
        )

    # 4. Non-compete enforceability (Contract Act Section 27)
    for m in _NON_COMPETE_RE.finditer(text):
        src = get_source("contract-act-s27")
        flags.append(
            RedFlag(
                category="non_compete_enforceability",
                severity="high",
                clause_excerpt=_excerpt(text, m),
                explanation=(
                    "Post-employment non-compete restrictions are generally void "
                    "and unenforceable in India under the restraint-of-trade "
                    "doctrine, though this offer letter includes one."
                ),
                citation=f"{src.statute}, {src.section}" if src else "",
            )
        )

    # 5. Training bond enforceability
    for m in _TRAINING_BOND_RE.finditer(text):
        src = get_source("contract-act-s74")
        flags.append(
            RedFlag(
                category="training_bond_enforceability",
                severity="medium",
                clause_excerpt=_excerpt(text, m),
                explanation=(
                    "Training bond amounts must be a genuine pre-estimate of the "
                    "employer's training cost; disproportionate amounts risk being "
                    "treated as an unenforceable penalty rather than damages."
                ),
                citation=f"{src.statute}, {src.section}" if src else "",
            )
        )

    return flags
