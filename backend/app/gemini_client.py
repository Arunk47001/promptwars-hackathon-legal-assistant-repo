"""Tiered Gemini model wrappers (C3).

Two thin call functions are exposed:
    - call_flash(prompt, ...)   -> Flash-class model (classification, PII
      triage, high-stakes trigger detection: cheap/fast tasks).
    - call_pro(prompt, ...)     -> Pro-class model (explanation, red-flag
      reasoning, cited Q&A synthesis, document ingestion/OCR-via-multimodal).

Both read the model name from config (app.config.Settings), never hardcoded,
so changing the model name is a config change only, per C3's acceptance
criteria.

Live-verification status (updated 2026-09-23)
-----------------------------------------------
A real Google AI Studio key was provided and the live path was smoke-tested
manually: text calls and the multimodal path (Kannada/English code-mixed
image -> transcription + translation) both returned correct, real model
output. See backend/docs/c4_ocr_spike_log.md for the full result and its
limits (tested against a clean synthetic image, not a real scanned document
yet).

Model names were also corrected as part of that check: the originally
configured `gemini-2.5-flash`/`gemini-2.5-pro` are retired for new users as
of this date. Config now uses `gemini-3.6-flash` (flash tier, confirmed) and
`gemini-pro-latest` (pro tier, confirmed as a valid name though it hit
free-tier quota during the check) — re-verify both against the live AI
Studio model picker periodically, since these strings move quickly.

Remaining gap: this confirms the SDK path and basic Kannada reading ability,
but NOT performance on a real photographed/scanned physical document (skew,
glare, handwriting, low resolution). Run
`backend/scripts/run_ocr_spike.py` against at least one real scanned sample
before fully trusting this in a demo.

Offline mock mode
------------------
When no API key is configured (or GEMINI_MOCK_MODE=true), every call is
served by a small deterministic mock so the rest of the pipeline (routing,
storage, PII masking, red-flag rules, guardrail wiring, frontend wiring) can
be built and tested end-to-end without a live key or network access. Mock
responses are clearly marked as such in their payload so they're never
mistaken for real model output.
"""
from __future__ import annotations

import base64
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from app.config import get_settings

logger = logging.getLogger("namma_nyaya.gemini")


@dataclass
class GeminiResponse:
    text: str
    model: str
    mock: bool
    raw: Optional[Any] = field(default=None, repr=False)


class GeminiCallError(RuntimeError):
    pass


def _get_client():
    """Lazily construct the google-genai client. Only called on the live
    (non-mock) path so importing this module never requires network access or
    a key."""
    from google import genai  # type: ignore

    settings = get_settings()
    return genai.Client(api_key=settings.gemini_api_key)


def _mock_response(model: str, prompt: str, kind: str) -> GeminiResponse:
    """Deterministic offline stand-in. Content is intentionally generic/
    templated — it exists only so downstream code paths (parsing, storage,
    guardrails) can be exercised locally, NOT as a claim about real model
    quality or accuracy."""
    text = (
        f"[MOCK-{kind.upper()} RESPONSE — no live Gemini call made; "
        f"GEMINI_MOCK_MODE is on or no API key configured]\n"
        f"prompt_preview={prompt[:200]!r}"
    )
    return GeminiResponse(text=text, model=model, mock=True, raw=None)


def call_flash(prompt: str, *, system_instruction: str | None = None) -> GeminiResponse:
    """Flash-class call: classification, PII-pattern triage, high-stakes
    trigger detection (C3, used by C8)."""
    settings = get_settings()
    model = settings.gemini_flash_model
    if settings.effective_mock_mode:
        return _mock_response(model, prompt, "flash")
    return _live_text_call(model, prompt, system_instruction)


def call_pro(prompt: str, *, system_instruction: str | None = None) -> GeminiResponse:
    """Pro-class call: explanation, red-flag reasoning, cited Q&A synthesis
    (C3, used by C10/C11/C13/C15)."""
    settings = get_settings()
    model = settings.gemini_pro_model
    if settings.effective_mock_mode:
        return _mock_response(model, prompt, "pro")
    return _live_text_call(model, prompt, system_instruction)


def call_pro_multimodal(
    *,
    file_bytes: bytes,
    mime_type: str,
    prompt: str,
) -> GeminiResponse:
    """Pro-class multimodal call used for document ingestion/OCR (C4/C7):
    sends the raw image/PDF bytes directly to Gemini alongside an extraction
    prompt, per the plan's Gemini-native ingestion decision.

    NOTE: per the plan's accepted PII-masking limitation (C6), masking is
    intentionally NOT applied before this call — raw document content
    (including any embedded PII) reaches Gemini in-flight. Masking only
    happens afterward, before persistence/logging.
    """
    settings = get_settings()
    model = settings.gemini_pro_model
    if settings.effective_mock_mode:
        # Deterministic mock "extraction" so ingestion plumbing (C7) is
        # testable without a live key. Clearly not real OCR output.
        mock_text = (
            "[MOCK EXTRACTION — offline mode, not a real Gemini OCR result]\n"
            "RENTAL AGREEMENT (sample)\n"
            "This agreement is made between the Landlord and the Tenant.\n"
            "1. Security Deposit: The Tenant shall pay a security deposit of "
            "10 months' rent.\n"
            "2. Lock-in Period: The Tenant shall not vacate before 11 months; "
            "the Landlord may terminate with 1 month notice.\n"
            "3. Notice Period: Tenant must give 3 months notice; Landlord "
            "must give 1 month notice.\n"
            "4. Painting and cleaning charges shall be deducted from the "
            "deposit regardless of the condition of the premises.\n"
        )
        return GeminiResponse(text=mock_text, model=model, mock=True, raw=None)
    return _live_multimodal_call(model, file_bytes, mime_type, prompt)


def _live_text_call(model: str, prompt: str, system_instruction: str | None) -> GeminiResponse:
    try:
        client = _get_client()
        kwargs: dict[str, Any] = {"model": model, "contents": prompt}
        if system_instruction:
            kwargs["config"] = {"system_instruction": system_instruction}
        response = client.models.generate_content(**kwargs)
        return GeminiResponse(text=response.text, model=model, mock=False, raw=response)
    except Exception as exc:  # pragma: no cover - live path, no network in sandbox
        logger.exception("Live Gemini text call failed")
        raise GeminiCallError(str(exc)) from exc


def _live_multimodal_call(
    model: str, file_bytes: bytes, mime_type: str, prompt: str
) -> GeminiResponse:
    try:
        from google.genai import types  # type: ignore

        client = _get_client()
        part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
        response = client.models.generate_content(
            model=model,
            contents=[part, prompt],
        )
        return GeminiResponse(text=response.text, model=model, mock=False, raw=response)
    except Exception as exc:  # pragma: no cover - live path, no network in sandbox
        logger.exception("Live Gemini multimodal call failed")
        raise GeminiCallError(str(exc)) from exc


def try_parse_json(text: str) -> Optional[dict]:
    """Best-effort JSON extraction from a model response (models sometimes
    wrap JSON in markdown fences)."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        return None
