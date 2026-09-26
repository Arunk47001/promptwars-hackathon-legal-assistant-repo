"""Env-based configuration loader.

Nothing in this module hardcodes a Gemini API key or a model version string —
per the plan's own caveat that exact Gemini model names move quickly, model
tier names are config values so swapping them requires no code edit (C1, C3).
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_pro_model: str = "gemini-2.5-pro"
    # Offline/deterministic mock mode — used when no live key is configured
    # (e.g. this sandboxed dev environment) so the rest of the pipeline can
    # still be built and exercised end-to-end. Must be turned off (and a real
    # key supplied) for any live demo. See app/gemini_client.py.
    gemini_mock_mode: bool = True

    cors_allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    host: str = "0.0.0.0"
    port: int = 8000

    # Security hardening (2026-09-26 remediation pass).
    # Server-side cap on uploaded document size, matching the frontend UI's
    # own "up to 10 MB" claim -- enforced here since nothing previously did.
    max_upload_bytes: int = 10 * 1024 * 1024
    # Basic per-IP rate limit applied to the Gemini-dependent endpoints
    # (document upload/ingest, classify, explain, red-flags, qa) to protect
    # the scarce/costly Gemini quota on this single-instance POC deployment.
    rate_limit_per_minute: int = 20

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]

    @property
    def effective_mock_mode(self) -> bool:
        """Mock mode is forced on whenever there is no API key, regardless of
        the explicit flag, so the app never silently tries a live call with an
        empty key."""
        return self.gemini_mock_mode or not self.gemini_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
