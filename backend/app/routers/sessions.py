"""Session resource routes.

A "session" here is a lightweight, channel-agnostic grouping of a user's
uploaded documents and Q&A history — deliberately not a browser
cookie/auth-session, so a future non-web channel (e.g. WhatsApp) could
create/reuse one via the same resource shape.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import SessionCreateResponse, SessionResponse
from app.storage import store

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionCreateResponse, status_code=201)
def create_session() -> SessionCreateResponse:
    record = store.create_session()
    return SessionCreateResponse(id=record.id, created_at=record.created_at)


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str) -> SessionResponse:
    record = store.get_session(session_id)
    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(
        id=record.id,
        created_at=record.created_at,
        document_ids=record.document_ids,
        qa_history=record.qa_history,
    )
