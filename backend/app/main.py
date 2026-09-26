"""FastAPI application entrypoint (C1).

Resource-oriented routing (/documents, /sessions, /actions) with OpenAPI
docs enabled at /docs. Config (Gemini key, model tiers, CORS origins) is
loaded from the environment via app.config.Settings — never hardcoded.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import get_settings
from app.rate_limit import limiter
from app.routers import actions, documents, health, sessions
from app.security_middleware import MaxBodySizeMiddleware, SecurityHeadersMiddleware

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

# Rate limiting (security remediation, 2026-09-26) -- see app/rate_limit.py.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Security response headers (security remediation, 2026-09-26).
app.add_middleware(SecurityHeadersMiddleware)

# Request-size fast-fail guard (security remediation, 2026-09-26): a little
# headroom above the actual upload cap for multipart boundary/header
# overhead; the authoritative per-file cap is enforced in the upload
# endpoint itself.
app.add_middleware(
    MaxBodySizeMiddleware, max_bytes=settings.max_upload_bytes + (1 * 1024 * 1024)
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
