"""Shared pydantic request/response schemas.

Kept channel-agnostic on purpose: no field here assumes a browser session,
cookie auth, or any web-page-specific shape (per the plan's locked
channel-agnostic architecture constraint).
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class _BaseModel(BaseModel):
    """Base with protected-namespace warning silenced: several response
    models legitimately need a `model_used` field (the Gemini model tier
    that served the response), which collides with pydantic's default
    `model_` protected prefix used for its own methods."""

    model_config = ConfigDict(protected_namespaces=())

DISCLAIMER_TEXT = (
    "Namma Nyaya provides general legal information to help you understand "
    "documents and next steps. It is NOT a substitute for advice from a "
    "licensed advocate, and nothing here should be treated as legal advice "
    "for your specific situation."
)

LEGAL_AID_MESSAGE = (
    "This looks like it may involve a high-stakes legal situation (e.g. "
    "arrest, criminal charge, custody, divorce, or a large property "
    "transaction). Namma Nyaya does not provide substantive help for these "
    "situations. Please consult a licensed advocate, or contact free legal "
    "aid: KSLSA (Karnataka State Legal Services Authority), your local DLSA "
    "(District Legal Services Authority), or call NALSA's toll-free helpline "
    "15100."
)


class GuardrailMeta(_BaseModel):
    disclaimer: str = DISCLAIMER_TEXT
    high_stakes: bool = False
    legal_aid_redirect: Optional[str] = None


class SessionCreateResponse(_BaseModel):
    id: str
    created_at: str


class SessionResponse(_BaseModel):
    id: str
    created_at: str
    document_ids: list[str]
    qa_history: list[dict]


class DocumentCreateResponse(_BaseModel):
    id: str
    filename: str
    content_type: str
    created_at: str
    guardrail: GuardrailMeta = Field(default_factory=GuardrailMeta)


class DocumentGetResponse(_BaseModel):
    id: str
    filename: str
    content_type: str
    masked_text: str
    document_type: Optional[str] = None
    high_stakes: Optional[bool] = None
    created_at: str


class ClassifyResponse(_BaseModel):
    document_id: str
    document_type: str
    high_stakes: bool
    high_stakes_reasons: list[str]
    guardrail: GuardrailMeta = Field(default_factory=GuardrailMeta)
    model_used: str
    mock: bool


class ExplanationLevels(_BaseModel):
    gist: str
    clause_by_clause: str
    legal_view: str
    citations: list[str] = Field(default_factory=list)


class ExplanationResponse(_BaseModel):
    document_id: str
    english: ExplanationLevels
    kannada: ExplanationLevels
    guardrail: GuardrailMeta = Field(default_factory=GuardrailMeta)
    model_used: str
    mock: bool


class RedFlag(_BaseModel):
    category: str
    severity: str  # "high" | "medium" | "low"
    clause_excerpt: str
    explanation: str
    citation: str


class RedFlagResponse(_BaseModel):
    document_id: str
    flags: list[RedFlag]
    guardrail: GuardrailMeta = Field(default_factory=GuardrailMeta)


class CompareRequest(_BaseModel):
    document_id_a: str
    document_id_b: str


class ClauseDiff(_BaseModel):
    field: str
    value_a: Optional[str]
    value_b: Optional[str]
    differs: bool
    red_flag_category: Optional[str] = None


class CompareResponse(_BaseModel):
    document_id_a: str
    document_id_b: str
    diffs: list[ClauseDiff]
    guardrail: GuardrailMeta = Field(default_factory=GuardrailMeta)


class QARequest(_BaseModel):
    question: str
    session_id: Optional[str] = None


class QAResponse(_BaseModel):
    document_id: str
    question: str
    answer: str
    citation: Optional[str]
    confidence: str  # "High" | "Medium" | "Low" | "N/A"
    i_dont_know: bool
    guardrail: GuardrailMeta = Field(default_factory=GuardrailMeta)


class LawMappingItem(_BaseModel):
    old_code: str
    old_section: str
    new_code: str
    new_section: str
    description: str


class LawMappingResponse(_BaseModel):
    query: str
    results: list[LawMappingItem]


class NavigatorPlaybookSummary(_BaseModel):
    id: str
    title: str
    description: str


class NavigatorPlaybookResponse(_BaseModel):
    id: str
    title: str
    forum: str
    required_documents: list[str]
    draft: str
    timeline: str
    cost: str
    guardrail: GuardrailMeta = Field(default_factory=GuardrailMeta)
