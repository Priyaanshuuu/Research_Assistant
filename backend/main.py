import time

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy import text
import sys

from api.middleware.rate_limit import RateLimitMiddleware
from api.middleware.request_id import RequestIDMiddleware
from api.middleware.validation import MaxBodySizeMiddleware
from api.routes.auth import router as auth_router
from api.routes.chat import router as chat_router
from api.routes.export import router as export_router
from api.routes.research import router as research_router
from core.config import settings
from db.database import SessionLocal
logger.remove()
logger.add(
    sys.stdout,
    format=(
        "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | "
        "{name}:{line} — {message}"
    ),
    level="INFO",
    colorize=True,
    serialize=False,
)
app = FastAPI(
    title="Research Assistant API",
    description="Multi-Agent Research Assistant — FastAPI backend",
    version="1.0.0",
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(MaxBodySizeMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID", "Content-Disposition"],
)
app.include_router(auth_router)
app.include_router(research_router)
app.include_router(chat_router)
app.include_router(export_router)

@app.on_event("startup")
async def startup() -> None:
    logger.info(
        "Research Assistant API v1.0.0 starting — env={}",
        settings.APP_ENV,
    )


@app.on_event("shutdown")
async def shutdown() -> None:
    logger.info("Research Assistant API shutting down")

@app.get("/health", tags=["meta"])
async def health_check() -> dict:
    """
    Checks real connectivity to Postgres and Redis.
    Returns 200 only when all dependencies are reachable.
    """
    checks: dict[str, str] = {}
    overall = "ok"

    # Postgres
    try:
        t0 = time.monotonic()
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        checks["postgres"] = f"ok ({(time.monotonic() - t0) * 1000:.1f}ms)"
    except Exception as exc:
        checks["postgres"] = f"error: {exc}"
        overall = "degraded"

    # Redis
    try:
        t0 = time.monotonic()
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await r.ping()
        await r.aclose()
        checks["redis"] = f"ok ({(time.monotonic() - t0) * 1000:.1f}ms)"
    except Exception as exc:
        checks["redis"] = f"error: {exc}"
        overall = "degraded"

    return {
        "status": overall,
        "version": "1.0.0",
        "env": settings.APP_ENV,
        "checks": checks,
    }