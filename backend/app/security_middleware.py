"""Security response headers + a request-size fast-fail guard (security
remediation, 2026-09-26).

This is a JSON API, not an HTML app, so the header set is kept minimal --
no CSP is added here since there is nothing here that renders HTML.
"""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer-when-downgrade")
        return response


class MaxBodySizeMiddleware:
    """Pure-ASGI middleware: rejects a request with a declared Content-Length
    above `max_bytes` before any multipart/body parsing happens, so an
    obviously oversized declared payload never reaches the form parser.

    This is a fast-fail safety net, not the authoritative limit -- requests
    with no Content-Length (e.g. chunked transfer-encoding) or a dishonest
    header still get bounded by the incremental, size-checked read in the
    document upload endpoint itself (see app/routers/documents.py).
    """

    def __init__(self, app, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        raw_length = headers.get(b"content-length")
        if raw_length is not None:
            try:
                declared_length = int(raw_length)
            except ValueError:
                declared_length = None
            if declared_length is not None and declared_length > self.max_bytes:
                response = JSONResponse(
                    {
                        "detail": (
                            "Request body exceeds the maximum allowed size of "
                            f"{self.max_bytes // (1024 * 1024)} MB."
                        )
                    },
                    status_code=413,
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)
