from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from core.config import settings
from api.routes.auth import router as auth_router

# ── Loguru configuration ────────────────────────────────────────────────────
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{line} — {message}",
    level="INFO",
    colorize=True,
    serialize=False,
)

# ── Lifespan Events ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Research Assistant API starting — env={}", settings.APP_ENV)
    yield
    # Shutdown
    logger.info("Research Assistant API shutting down")


# ── Application ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Research Assistant API",
    description="Multi-Agent Research Assistant — FastAPI backend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,  # ← ADD THIS
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth_router)

# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/health", tags=["meta"])
async def health_check() -> dict:
    return {"status": "ok", "version": "0.1.0", "env": settings.APP_ENV}