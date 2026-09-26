"""Basic per-IP rate limiting (security remediation, 2026-09-26).

The public API has no auth and is backed by a scarce/costly Gemini quota, so
every Gemini-dependent endpoint (document upload/ingest, classify, explain,
red-flags, qa) should have a sane per-IP request cap. This is a single-instance
Render deployment, so an in-memory limiter (slowapi/limits) is sufficient --
no Redis/distributed state needed for this POC.
"""
from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings

limiter = Limiter(key_func=get_remote_address)

# Built once from config at import time (consistent with how other
# env-derived settings, e.g. CORS origins, are already loaded once at
# startup elsewhere in this app).
RATE_LIMIT = f"{get_settings().rate_limit_per_minute}/minute"
