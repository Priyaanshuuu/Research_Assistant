# REPLACE THIS FILE — mounts all routers and rate limit middleware

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from core.config import settings
from api.routes.auth import router as auth_router
from api.routes.research import router as research_router
from api.routes.chat import router as chat_router
from api.routes.export import router as export_router
from api.middleware.rate_limit import RateLimitMiddleware

# ── Loguru ───────────────────────────────────────────────────────────────────
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{line} — {message}",
    level="INFO",
    colorize=True,
    serialize=False,
)

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Research Assistant API",
    description="Multi-Agent Research Assistant — FastAPI backend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware (order matters — rate limit before CORS) ───────────────────────
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(research_router)
app.include_router(chat_router)
app.include_router(export_router)


# ── Lifecycle ─────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup() -> None:
    logger.info("Research Assistant API starting — env={}", settings.APP_ENV)


@app.on_event("shutdown")
async def shutdown() -> None:
    logger.info("Research Assistant API shutting down")


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["meta"])
async def health_check() -> dict:
    return {"status": "ok", "version": "0.1.0", "env": settings.APP_ENV}