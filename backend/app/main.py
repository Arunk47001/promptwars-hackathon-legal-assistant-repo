"""FastAPI application entrypoint (C1).

Resource-oriented routing (/documents, /sessions, /actions) with OpenAPI
docs enabled at /docs. Config (Gemini key, model tiers, CORS origins) is
loaded from the environment via app.config.Settings — never hardcoded.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import actions, documents, health, sessions

settings = get_settings()

app = FastAPI(
    title="Namma Nyaya API",
    description=(
        "Channel-agnostic legal-companion API for Bengaluru rental "
        "agreements and offer letters. Resource-oriented: /documents, "
        "/sessions, /actions."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(sessions.router)
app.include_router(documents.router)
app.include_router(actions.router)
