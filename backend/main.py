from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys
from sqlalchemy.orm import Session

from core.config import settings
from api.routes.auth import router as auth_router
from db.database import engine, get_db
from db import models
from db import schemas

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
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")
    yield
    # Shutdown
    logger.info("Research Assistant API shutting down")


# ── Dependencies ─────────────────────────────────────────────────────────────
async def get_current_user(db: Session = Depends(get_db)) -> schemas.UserResponse:
    """Get current authenticated user from request context"""
    # TODO: Implement JWT/token verification
    # For now, placeholder - should extract from Authorization header
    raise HTTPException(status_code=401, detail="Not authenticated")


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


# ── Research Session Routes ──────────────────────────────────────────────────
@app.post("/research-sessions/", response_model=schemas.ResearchSessionResponse, tags=["research"])
async def create_research_session(
    session_data: schemas.ResearchSessionCreate,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new research session for the current user"""
    db_session = models.ResearchSession(
        user_id=current_user.id,
        topic=session_data.topic,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@app.get("/research-sessions/", response_model=list[schemas.ResearchSessionResponse], tags=["research"])
async def list_research_sessions(
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all research sessions for the current user"""
    sessions = (
        db.query(models.ResearchSession)
        .filter(models.ResearchSession.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return sessions


@app.get(
    "/research-sessions/{session_id}", 
    response_model=schemas.ResearchSessionDetail, 
    tags=["research"]
)
async def get_research_session(
    session_id: str,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed research session with chat history and agent events"""
    db_session = (
        db.query(models.ResearchSession)
        .filter(
            models.ResearchSession.id == session_id,
            models.ResearchSession.user_id == current_user.id,
        )
        .first()
    )
    if not db_session:
        raise HTTPException(status_code=404, detail="Research session not found")
    return db_session


@app.patch(
    "/research-sessions/{session_id}",
    response_model=schemas.ResearchSessionResponse,
    tags=["research"],
)
async def update_research_session(
    session_id: str,
    updates: schemas.ResearchSessionUpdate,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update research session status and results"""
    db_session = (
        db.query(models.ResearchSession)
        .filter(
            models.ResearchSession.id == session_id,
            models.ResearchSession.user_id == current_user.id,
        )
        .first()
    )
    if not db_session:
        raise HTTPException(status_code=404, detail="Research session not found")
    
    # Update only provided fields
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_session, field, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session


# ── Chat Message Routes ──────────────────────────────────────────────────────
@app.post(
    "/research-sessions/{session_id}/messages/",
    response_model=schemas.ChatMessageResponse,
    tags=["chat"],
)
async def create_chat_message(
    session_id: str,
    message: schemas.ChatMessageCreate,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a message to research session chat"""
    # Verify session exists and belongs to user
    db_session = (
        db.query(models.ResearchSession)
        .filter(
            models.ResearchSession.id == session_id,
            models.ResearchSession.user_id == current_user.id,
        )
        .first()
    )
    if not db_session:
        raise HTTPException(status_code=404, detail="Research session not found")
    
    db_message = models.ChatMessage(
        session_id=session_id,
        role=message.role,
        content=message.content,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@app.get(
    "/research-sessions/{session_id}/messages/",
    response_model=list[schemas.ChatMessageResponse],
    tags=["chat"],
)
async def list_chat_messages(
    session_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List chat messages for a research session"""
    # Verify session belongs to user
    db_session = (
        db.query(models.ResearchSession)
        .filter(
            models.ResearchSession.id == session_id,
            models.ResearchSession.user_id == current_user.id,
        )
        .first()
    )
    if not db_session:
        raise HTTPException(status_code=404, detail="Research session not found")
    
    messages = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id == session_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return messages


# ── Agent Event Routes ───────────────────────────────────────────────────────
@app.get(
    "/research-sessions/{session_id}/events/",
    response_model=list[schemas.AgentEventResponse],
    tags=["agents"],
)
async def list_agent_events(
    session_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List agent events for a research session"""
    # Verify session belongs to user
    db_session = (
        db.query(models.ResearchSession)
        .filter(
            models.ResearchSession.id == session_id,
            models.ResearchSession.user_id == current_user.id,
        )
        .first()
    )
    if not db_session:
        raise HTTPException(status_code=404, detail="Research session not found")
    
    events = (
        db.query(models.AgentEvent)
        .filter(models.AgentEvent.session_id == session_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return events