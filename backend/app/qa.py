"""Cited Q&A endpoint logic (C13).

Answers are grounded ONLY in the curated source set (C9) plus the
document's own clauses. Confidence indicator is rule-based
(High/Medium/Low), per the task breakdown's adopted default (Notes and
assumptions):
    - High: an exact statutory citation from the curated set matches a
      keyword in both the question and the document text.
    - Medium: a curated source matches the question OR the document text,
      but not both (a paraphrased/partial match).
    - Low / "I don't know": nothing in the curated set supports the
      question at all — returned as an explicit first-class "I don't know"
      response, never a fabricated answer (C13, C16).
"""
from __future__ import annotations

from dataclasses import dataclass

from app.gemini_client import call_pro
from app.legal_sources import CONTEXT_BLOCK, find_relevant_sources_strict
from app.models import QAResponse

I_DONT_KNOW_TEXT = (
    "I don't know — none of Namma Nyaya's curated legal sources or your "
    "document's own text directly support an answer to this question. "
    "Please consult a lawyer or free legal aid (KSLSA/DLSA/NALSA 15100) for "
    "a definitive answer."
)


@dataclass
class QAResult:
    answer: str
    citation: str | None
    confidence: str
    i_dont_know: bool


def answer_question(*, document_text: str, question: str) -> QAResult:
    from app.config import get_settings

    settings = get_settings()

    # Confidence is driven by whether the QUESTION itself maps to a curated
    # source at all (an unrelated question — e.g. "What is the capital of
    # France?" — must fall back to "I don't know" even though the document
    # text itself will almost always match *something*, since it's a rental
    # agreement/offer letter full of deposit/notice/lock-in language).
    question_sources = find_relevant_sources_strict(question)
    document_sources = find_relevant_sources_strict(document_text)

    if not question_sources:
        return QAResult(
            answer=I_DONT_KNOW_TEXT,
            citation=None,
            confidence="Low",
            i_dont_know=True,
        )

    matched_both = [s for s in question_sources if s in document_sources]
    if matched_both:
        confidence = "High"
        chosen = matched_both[0]
    else:
        confidence = "Medium"
        chosen = question_sources[0]

    citation = f"{chosen.statute}, {chosen.section}"

    if settings.effective_mock_mode:
        answer = (
            f"[MOCK ANSWER — offline mode] Based on {citation}: {chosen.text[:220]}"
        )
    else:
        prompt = (
            "Answer the user's question using ONLY the curated legal sources "
            "and the document text below. Cite the source [id] you rely on. "
            "If nothing supports an answer, say so explicitly rather than "
            "guessing.\n\n"
            f"{CONTEXT_BLOCK}\n\nDOCUMENT TEXT:\n{document_text[:4000]}\n\n"
            f"QUESTION: {question}"
        )
        response = call_pro(prompt)
        answer = response.text

    return QAResult(
        answer=answer,
        citation=citation,
        confidence=confidence,
        i_dont_know=False,
    )
