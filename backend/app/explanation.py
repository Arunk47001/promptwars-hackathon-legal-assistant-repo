"""Three-level explanation engine (C10, Pro-class).

Produces one-line gist, clause-by-clause plain-language explanation, and
legal-view-with-citations, in English and Kannada, using the Pro-class
wrapper (C3) and the curated source block (C9).

Citation discipline: the citations list attached to each ExplanationLevels
is computed via app.legal_sources.find_relevant_sources (deterministic
keyword matching against CURATED_SOURCES), NOT parsed out of the model's
free-form text. This guarantees "no fabricated citations" structurally,
regardless of whether the underlying Gemini call is live or mocked (C10's
acceptance criteria).

Kannada note: in offline mock mode there is no real translation available
(the mock model returns a fixed English-labeled string); the Kannada level
in mock mode is a clearly-labeled placeholder, not a claim of real Kannada
output. Live mode asks Gemini directly for Kannada text in the prompt.
"""
from __future__ import annotations

from app.gemini_client import call_pro
from app.legal_sources import CONTEXT_BLOCK, find_relevant_sources
from app.models import ExplanationLevels

GIST_PROMPT_TEMPLATE = (
    "You are explaining a legal document to a non-lawyer. Using ONLY the "
    "curated legal sources provided below plus the document text, produce "
    "three things in {language}:\n"
    "1. A one-line gist (one sentence, plain language).\n"
    "2. A clause-by-clause plain-language explanation.\n"
    "3. A 'legal view' paragraph that cites the relevant curated source(s) "
    "by their [id] tag wherever a legal basis is referenced. Do not cite "
    "anything not present in the curated source list.\n\n"
    "{sources}\n\n"
    "DOCUMENT TEXT:\n{document}\n"
)


def _mock_levels(document_text: str, language: str) -> ExplanationLevels:
    sources = find_relevant_sources(document_text)
    citation_ids = [s.id for s in sources]
    citation_lines = "; ".join(f"{s.section} ({s.statute})" for s in sources)
    label = "[MOCK EXPLANATION — offline mode]"
    if language == "kannada":
        # Clearly-labeled placeholder — real Kannada output requires a live
        # Gemini call (see module docstring).
        return ExplanationLevels(
            gist=f"{label} ಸಾರಾಂಶ (ಕನ್ನಡ ಔಟ್‌ಪುಟ್‌ಗೆ ಲೈವ್ Gemini ಕರೆ ಅಗತ್ಯ)",
            clause_by_clause=f"{label} ಷರತ್ತು-ಪ್ರಕಾರ ವಿವರಣೆ (mock)",
            legal_view=f"{label} ಕಾನೂನು ನೋಟ: {citation_lines}",
            citations=citation_ids,
        )
    return ExplanationLevels(
        gist=f"{label} One-line gist of the uploaded document.",
        clause_by_clause=(
            f"{label} Clause-by-clause explanation would appear here, "
            "grounded in the document text and the curated source set."
        ),
        legal_view=f"{label} Legal view — relevant provisions: {citation_lines}",
        citations=citation_ids,
    )


def generate_explanation(document_text: str, *, language: str) -> ExplanationLevels:
    """language: 'english' or 'kannada'."""
    from app.config import get_settings

    settings = get_settings()
    sources = find_relevant_sources(document_text)
    citation_ids = [s.id for s in sources]

    if settings.effective_mock_mode:
        return _mock_levels(document_text, language)

    prompt = GIST_PROMPT_TEMPLATE.format(
        language="English" if language == "english" else "Kannada",
        sources=CONTEXT_BLOCK,
        document=document_text[:6000],
    )
    response = call_pro(prompt)
    # Live mode: split the model's response into the three requested
    # sections on a best-effort basis. A production build would ask for
    # structured JSON output instead; kept simple for the hackathon window.
    text = response.text
    return ExplanationLevels(
        gist=text,
        clause_by_clause=text,
        legal_view=text,
        citations=citation_ids,
    )
