"""Standalone /actions routes not scoped to a single document resource:
compare (C12), law-mapping (C14), and navigator (C15).

Kept under /actions rather than page-shaped paths (e.g. not
"/compare-page") per the plan's channel-agnostic constraint.
"""
from __future__ import annotations

from fastapi import APIRouter, Body, HTTPException

from app.compare import compare_documents
from app.guardrails import build_guardrail
from app.law_mapping import lookup_any
from app.models import (
    CompareRequest,
    CompareResponse,
    LawMappingItem,
    LawMappingResponse,
    NavigatorPlaybookResponse,
    NavigatorPlaybookSummary,
)
from app.navigator import list_playbooks, run_playbook
from app.storage import store

router = APIRouter(prefix="/actions", tags=["actions"])


@router.post("/compare", response_model=CompareResponse)
def compare(body: CompareRequest) -> CompareResponse:
    doc_a = store.get_document(body.document_id_a)
    doc_b = store.get_document(body.document_id_b)
    if not doc_a or not doc_b:
        raise HTTPException(status_code=404, detail="One or both documents not found")

    diffs = compare_documents(doc_a.masked_text, doc_b.masked_text)
    return CompareResponse(
        document_id_a=body.document_id_a,
        document_id_b=body.document_id_b,
        diffs=diffs,
        guardrail=build_guardrail(high_stakes=False),
    )


@router.get("/law-mapping", response_model=LawMappingResponse)
def law_mapping(section: str, code: str | None = None) -> LawMappingResponse:
    results = lookup_any(section, code_hint=code)
    return LawMappingResponse(
        query=section,
        results=[
            LawMappingItem(
                old_code=m.old_code.value,
                old_section=m.old_section,
                new_code=m.new_code.value,
                new_section=m.new_section,
                description=m.description,
            )
            for m in results
        ],
    )


@router.get("/navigator/playbooks", response_model=list[NavigatorPlaybookSummary])
def navigator_playbooks() -> list[NavigatorPlaybookSummary]:
    return [
        NavigatorPlaybookSummary(id=p.id, title=p.title, description=p.description)
        for p in list_playbooks()
    ]


@router.post("/navigator/{playbook_id}", response_model=NavigatorPlaybookResponse)
def navigator_run(
    playbook_id: str, facts: dict = Body(default_factory=dict)
) -> NavigatorPlaybookResponse:
    result = run_playbook(playbook_id, facts)
    if not result:
        raise HTTPException(status_code=404, detail="Unknown playbook id")
    return NavigatorPlaybookResponse(
        id=result.id,
        title=result.title,
        forum=result.forum,
        required_documents=result.required_documents,
        draft=result.draft,
        timeline=result.timeline,
        cost=result.cost,
        guardrail=build_guardrail(high_stakes=False),
    )
