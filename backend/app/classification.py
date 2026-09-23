"""Classification + high-stakes trigger detection (C8, Flash-class).

Per the task breakdown's own framing (Notes and assumptions / C8's
acceptance criteria), this is explicitly an MVP-level "detect obvious cases"
implementation, not a rigorously tested detector:

    "Known limitation: MVP-level keyword/classification detection, not a
    rigorously tested detector."

Implementation approach: deterministic keyword/pattern rules decide the
actual document-type label and high-stakes flag (so behavior is testable
without a live Gemini call and reproducible for the acceptance-criteria
test), while a Flash-class Gemini call is also made per C3/C8's intent (to
produce a human-readable rationale and to exercise the Flash-class wrapper
end-to-end). In offline mock mode this call returns a labeled mock string;
the flag/label returned to the caller is always the deterministic rule
result, never parsed out of free-form model text, precisely to avoid
silently-wrong parsing of an ungrounded response.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.gemini_client import call_flash

HIGH_STAKES_KEYWORDS = {
    "arrest": "mentions arrest",
    "criminal charge": "mentions a criminal charge",
    "criminal case": "mentions a criminal case",
    "fir": "mentions an FIR",
    "custody": "mentions child/legal custody",
    "divorce": "mentions divorce",
    "domestic violence": "mentions domestic violence",
    "sale deed": "mentions a large property/sale-deed transaction",
    "crore": "mentions a large monetary/property value (crore)",
}

RENTAL_KEYWORDS = ["landlord", "tenant", "lease", "rent", "security deposit", "lessor", "lessee"]
OFFER_LETTER_KEYWORDS = [
    "offer of employment",
    "ctc",
    "joining date",
    "designation",
    "employer",
    "employee",
    "notice period",
    "non-compete",
    "probation",
]


@dataclass
class ClassificationResult:
    document_type: str
    high_stakes: bool
    high_stakes_reasons: list[str] = field(default_factory=list)
    model_used: str = ""
    mock: bool = True


def classify_document(text: str) -> ClassificationResult:
    lowered = text.lower()

    reasons = [msg for kw, msg in HIGH_STAKES_KEYWORDS.items() if kw in lowered]
    high_stakes = bool(reasons)

    rental_score = sum(1 for kw in RENTAL_KEYWORDS if kw in lowered)
    offer_score = sum(1 for kw in OFFER_LETTER_KEYWORDS if kw in lowered)

    if rental_score == 0 and offer_score == 0:
        document_type = "unknown"
    elif rental_score >= offer_score:
        document_type = "rental_agreement"
    else:
        document_type = "offer_letter"

    prompt = (
        "Classify this legal document as either a rental agreement or an "
        "employment offer letter, and note in one sentence whether it "
        "appears to touch a high-stakes legal situation (arrest, criminal "
        "charge, custody, divorce, or a large property transaction). "
        f"Document text:\n\n{text[:4000]}"
    )
    response = call_flash(prompt)

    return ClassificationResult(
        document_type=document_type,
        high_stakes=high_stakes,
        high_stakes_reasons=reasons,
        model_used=response.model,
        mock=response.mock,
    )
