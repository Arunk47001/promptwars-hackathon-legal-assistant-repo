"""Document resource routes (C7-C8, C10-C11, C13).

Resource-oriented per the plan's channel-agnostic constraint:
    POST /documents                      -- ingest (C7)
    GET  /documents/{id}                 -- fetch masked text + metadata
    GET  /documents                      -- list
    POST /documents/{id}/actions/classify    -- C8
    POST /documents/{id}/actions/explain     -- C10
    POST /documents/{id}/actions/red-flags   -- C11
    POST /documents/{id}/actions/qa          -- C13

None of these assume a browser session or web-only auth model; document IDs
are opaque UUIDs usable by any channel.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Form, HTTPException, UploadFile

from app.classification import classify_document
from app.explanation import generate_explanation
from app.guardrails import build_guardrail
from app.ingestion import UnsupportedFileTypeError, ingest_document
from app.models import (
    ClassifyResponse,
    DocumentCreateResponse,
    DocumentGetResponse,
    ExplanationResponse,
    QARequest,
    QAResponse,
    RedFlagResponse,
)
from app.pii import mask_pii
from app.qa import answer_question
from app.red_flags import detect_red_flags
from app.storage import store

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentCreateResponse, status_code=201)
async def create_document(
    file: UploadFile,
    session_id: Optional[str] = Form(default=None),
) -> DocumentCreateResponse:
    file_bytes = await file.read()
    content_type = file.content_type or "application/octet-stream"

    try:
        result = ingest_document(file_bytes=file_bytes, content_type=content_type)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # PII masking (C6) applied here, before persistence — NOT before the
    # ingestion call above, per the plan's accepted POC-level limitation.
    masked_text = mask_pii(result.extracted_text)

    record = store.create_document(
        filename=file.filename or "unknown",
        content_type=content_type,
        masked_text=masked_text,
        session_id=session_id,
    )
    return DocumentCreateResponse(
        id=record.id,
        filename=record.filename,
        content_type=record.content_type,
        created_at=record.created_at,
        guardrail=build_guardrail(high_stakes=False),
    )


@router.get("", response_model=list[DocumentGetResponse])
def list_documents() -> list[DocumentGetResponse]:
    return [
        DocumentGetResponse(
            id=d.id,
            filename=d.filename,
            content_type=d.content_type,
            masked_text=d.masked_text,
            document_type=d.document_type,
            high_stakes=d.high_stakes,
            created_at=d.created_at,
        )
        for d in store.list_documents()
    ]


@router.get("/{document_id}", response_model=DocumentGetResponse)
def get_document(document_id: str) -> DocumentGetResponse:
    record = store.get_document(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentGetResponse(
        id=record.id,
        filename=record.filename,
        content_type=record.content_type,
        masked_text=record.masked_text,
        document_type=record.document_type,
        high_stakes=record.high_stakes,
        created_at=record.created_at,
    )


def _get_or_404(document_id: str):
    record = store.get_document(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    return record


@router.post("/{document_id}/actions/classify", response_model=ClassifyResponse)
def classify(document_id: str) -> ClassifyResponse:
    record = _get_or_404(document_id)
    result = classify_document(record.masked_text)
    record.document_type = result.document_type
    record.high_stakes = result.high_stakes
    record.high_stakes_reasons = result.high_stakes_reasons
    return ClassifyResponse(
        document_id=document_id,
        document_type=result.document_type,
        high_stakes=result.high_stakes,
        high_stakes_reasons=result.high_stakes_reasons,
        guardrail=build_guardrail(high_stakes=result.high_stakes),
        model_used=result.model_used,
        mock=result.mock,
    )


@router.post("/{document_id}/actions/explain", response_model=ExplanationResponse)
def explain(document_id: str) -> ExplanationResponse:
    record = _get_or_404(document_id)
    if record.high_stakes is None:
        classify(document_id)
        record = _get_or_404(document_id)

    if record.high_stakes:
        # Per C16: high-stakes documents get the legal-aid redirect instead
        # of substantive explanation content.
        guardrail = build_guardrail(high_stakes=True)
        return _high_stakes_explanation_response(document_id, guardrail)

    english = generate_explanation(record.masked_text, language="english")
    kannada = generate_explanation(record.masked_text, language="kannada")
    from app.config import get_settings

    settings = get_settings()
    return ExplanationResponse(
        document_id=document_id,
        english=english,
        kannada=kannada,
        guardrail=build_guardrail(high_stakes=False),
        model_used=settings.gemini_pro_model,
        mock=settings.effective_mock_mode,
    )


def _high_stakes_explanation_response(document_id: str, guardrail) -> ExplanationResponse:
    from app.models import ExplanationLevels

    redirect_levels = ExplanationLevels(
        gist=guardrail.legal_aid_redirect,
        clause_by_clause=guardrail.legal_aid_redirect,
        legal_view=guardrail.legal_aid_redirect,
        citations=[],
    )
    return ExplanationResponse(
        document_id=document_id,
        english=redirect_levels,
        kannada=redirect_levels,
        guardrail=guardrail,
        model_used="",
        mock=True,
    )


@router.post("/{document_id}/actions/red-flags", response_model=RedFlagResponse)
def red_flags(document_id: str) -> RedFlagResponse:
    record = _get_or_404(document_id)
    if record.high_stakes is None:
        classify(document_id)
        record = _get_or_404(document_id)

    if record.high_stakes:
        return RedFlagResponse(
            document_id=document_id,
            flags=[],
            guardrail=build_guardrail(high_stakes=True),
        )

    flags = detect_red_flags(record.masked_text)
    return RedFlagResponse(
        document_id=document_id,
        flags=flags,
        guardrail=build_guardrail(high_stakes=False),
    )


@router.post("/{document_id}/actions/qa", response_model=QAResponse)
def qa(document_id: str, body: QARequest) -> QAResponse:
    record = _get_or_404(document_id)
    if record.high_stakes is None:
        classify(document_id)
        record = _get_or_404(document_id)

    guardrail = build_guardrail(high_stakes=bool(record.high_stakes))
    if record.high_stakes:
        return QAResponse(
            document_id=document_id,
            question=body.question,
            answer=guardrail.legal_aid_redirect or "",
            citation=None,
            confidence="N/A",
            i_dont_know=False,
            guardrail=guardrail,
        )

    result = answer_question(document_text=record.masked_text, question=body.question)

    if body.session_id:
        session = store.get_session(body.session_id)
        if session:
            session.qa_history.append(
                {
                    "document_id": document_id,
                    "question": body.question,
                    "answer": result.answer,
                    "confidence": result.confidence,
                    "i_dont_know": result.i_dont_know,
                }
            )

    return QAResponse(
        document_id=document_id,
        question=body.question,
        answer=result.answer,
        citation=result.citation,
        confidence=result.confidence,
        i_dont_know=result.i_dont_know,
        guardrail=guardrail,
    )
