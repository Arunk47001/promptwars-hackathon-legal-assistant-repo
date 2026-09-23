"""Document ingestion pipeline (C4 primary path / C7 endpoint logic).

Sends the uploaded image/PDF directly to the Gemini Pro-class multimodal
wrapper (C3) for text extraction, per the plan's locked Gemini-native
ingestion decision (Decisions resolved #2).

*** C4 GO/NO-GO STATUS: NOT YET LIVE-VALIDATED ***
The task breakdown calls C4 a "day-1 go/no-go spike": assemble 5-10 sample
documents (clean English, clean Kannada, code-mixed, low-quality scans),
send each through this pipeline, compare against a human reference
transcription, and record an explicit go/no-go call before building
ingestion-dependent features on top of it.

This sandboxed environment has no Gemini API key and cannot make live model
calls, so that spike could NOT be run here. What this module provides
instead:
    - A clean, correct implementation of the ingestion call itself (prompt,
      image/PDF handling via app.gemini_client.call_pro_multimodal,
      structured-output parsing) so the spike is easy to run manually the
      moment a real key is available.
    - `scripts/run_ocr_spike.py` (see backend/scripts/) — a runnable harness
      that takes a directory of sample documents plus reference
      transcriptions and produces the spike log the task requires.
    - An explicit placeholder go/no-go record in
      `backend/docs/c4_ocr_spike_log.md`, marked UNVALIDATED, not a
      fabricated "go".

Per the run instructions: downstream tasks (C7-C13) are built on the
Gemini-native ("go") path, since that is the plan's primary path and no
result exists yet to justify branching to C5 (Vision fallback). This is a
documented assumption, not a verified result — flagged again in the status
report.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.gemini_client import GeminiResponse, call_pro_multimodal

EXTRACTION_PROMPT = (
    "You are extracting text from a scanned legal document (a rental "
    "agreement or an employment offer letter) for a legal-explanation tool. "
    "The document may be in English, Kannada, or a mix of both, and may be a "
    "low-quality photo or scan.\n\n"
    "Task: Transcribe the FULL text of the document as accurately as "
    "possible, preserving clause/paragraph structure and numbering where "
    "present. If a word or phrase is illegible, mark it as [illegible] "
    "rather than guessing. Do not summarize, translate, or omit content — "
    "this is a verbatim extraction step; explanation happens separately.\n\n"
    "Return only the transcribed text, no commentary."
)

SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
}


@dataclass
class IngestionResult:
    extracted_text: str
    model_used: str
    mock: bool


class UnsupportedFileTypeError(ValueError):
    pass


def ingest_document(*, file_bytes: bytes, content_type: str) -> IngestionResult:
    """Run the primary Gemini-native ingestion path (C4's "go" branch,
    pending live validation) over an uploaded document's raw bytes.

    Raises UnsupportedFileTypeError for content types outside the MVP's
    supported set (PDF/image), so the caller (C7's endpoint) can return a
    clean 4xx instead of forwarding a bad request to Gemini.
    """
    if content_type not in SUPPORTED_MIME_TYPES:
        raise UnsupportedFileTypeError(
            f"Unsupported content type '{content_type}'. Supported: "
            f"{sorted(SUPPORTED_MIME_TYPES)}"
        )

    response: GeminiResponse = call_pro_multimodal(
        file_bytes=file_bytes,
        mime_type=content_type,
        prompt=EXTRACTION_PROMPT,
    )
    return IngestionResult(
        extracted_text=response.text,
        model_used=response.model,
        mock=response.mock,
    )
