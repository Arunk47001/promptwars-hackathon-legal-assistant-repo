"""Responsible-AI guardrail wiring (C16).

- Standing "information, not advice" disclaimer attached as API response
  metadata on every relevant response (see app.models.GuardrailMeta).
- When a document's high-stakes flag (C8) is true, substantive
  explanation/Q&A endpoints return the legal-aid redirect message instead of
  real content.
- C13's "I don't know" is already a first-class response shape (see
  app.qa.answer_question / QAResponse.i_dont_know), not an afterthought
  bolted on here.
"""
from __future__ import annotations

from app.models import LEGAL_AID_MESSAGE, GuardrailMeta


def build_guardrail(*, high_stakes: bool) -> GuardrailMeta:
    return GuardrailMeta(
        high_stakes=high_stakes,
        legal_aid_redirect=LEGAL_AID_MESSAGE if high_stakes else None,
    )
