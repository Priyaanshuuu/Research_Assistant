"""
Redis-backed sliding-window rate limiter as a FastAPI middleware.
Limits by user_id (extracted from JWT) or by IP for unauthenticated routes.
"""
from fastapi import Request, Response
from jose import jwt, JWTError
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.config import settings
from services.redis_service import increment_rate_limit

# (max_requests, window_seconds) per route prefix
RATE_LIMIT_RULES: dict[str, tuple[int, int]] = {
    "/research/start": (10, 60),       # 10 starts per minute
    "/chat":           (30, 60),       # 30 chat messages per minute
    "/auth/register":  (5,  60),       # 5 registrations per minute per IP
    "/auth/login":     (10, 60),       # 10 login attempts per minute
}

DEFAULT_LIMIT = (60, 60)              # 60 requests/min for all other routes


def _extract_identity(request: Request) -> str:
    """Returns user_id from JWT if present, otherwise the client IP."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        try:
            payload = jwt.decode(
                auth.removeprefix("Bearer "),
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            uid = payload.get("sub")
            if uid:
                return f"user:{uid}"
        except JWTError:
            pass
    return f"ip:{request.client.host if request.client else 'unknown'}"


def _get_limit(path: str) -> tuple[int, int]:
    for prefix, rule in RATE_LIMIT_RULES.items():
        if path.startswith(prefix):
            return rule
    return DEFAULT_LIMIT


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health checks and static Next.js internals
        if request.url.path in ("/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        identity = _extract_identity(request)
        max_requests, window = _get_limit(request.url.path)
        rl_key = f"{request.url.path}:{identity}"

        try:
            count = await increment_rate_limit(rl_key, window_seconds=window)
        except Exception as exc:
            logger.warning("[rate_limit] Redis error — allowing request: {}", exc)
            return await call_next(request)

        if count > max_requests:
            logger.warning(
                "[rate_limit] BLOCKED {} {} — {}/{} in {}s",
                identity,
                request.url.path,
                count,
                max_requests,
                window,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests",
                    "retry_after_seconds": window,
                },
                headers={"Retry-After": str(window)},
            )

        return await call_next(request)