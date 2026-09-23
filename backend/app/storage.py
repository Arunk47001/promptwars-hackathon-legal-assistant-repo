"""In-memory storage for the hackathon POC.

Per spec's own data-retention framing ("allow processing without storing
documents" is a principle, not yet a locked decision) and the hackathon time
box, this POC uses a simple process-local in-memory store keyed by UUID
rather than a real database. This is sufficient to satisfy the coder-lane
acceptance criteria (upload -> get by id) and is easy to swap for a real DB
later without changing the resource-oriented API shape.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class DocumentRecord:
    id: str
    filename: str
    content_type: str
    masked_text: str
    document_type: Optional[str] = None
    high_stakes: Optional[bool] = None
    high_stakes_reasons: list[str] = field(default_factory=list)
    session_id: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class SessionRecord:
    id: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    document_ids: list[str] = field(default_factory=list)
    qa_history: list[dict] = field(default_factory=list)


class InMemoryStore:
    def __init__(self) -> None:
        self.documents: dict[str, DocumentRecord] = {}
        self.sessions: dict[str, SessionRecord] = {}

    # -- documents ---------------------------------------------------
    def create_document(
        self,
        *,
        filename: str,
        content_type: str,
        masked_text: str,
        session_id: Optional[str] = None,
    ) -> DocumentRecord:
        doc_id = str(uuid.uuid4())
        record = DocumentRecord(
            id=doc_id,
            filename=filename,
            content_type=content_type,
            masked_text=masked_text,
            session_id=session_id,
        )
        self.documents[doc_id] = record
        if session_id and session_id in self.sessions:
            self.sessions[session_id].document_ids.append(doc_id)
        return record

    def get_document(self, doc_id: str) -> Optional[DocumentRecord]:
        return self.documents.get(doc_id)

    def list_documents(self) -> list[DocumentRecord]:
        return list(self.documents.values())

    # -- sessions ------------------------------------------------------
    def create_session(self) -> SessionRecord:
        session_id = str(uuid.uuid4())
        record = SessionRecord(id=session_id)
        self.sessions[session_id] = record
        return record

    def get_session(self, session_id: str) -> Optional[SessionRecord]:
        return self.sessions.get(session_id)


# Process-wide singleton store (fine for a single-instance hackathon POC).
store = InMemoryStore()
