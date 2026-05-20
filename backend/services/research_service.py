"""
Owns all database reads and writes during a research session lifecycle.
Called by the background task in research.py — keeps route handlers thin.
"""
import uuid
from typing import Any

from loguru import logger
from sqlalchemy.orm import Session

from db.models import AgentEvent, ResearchSession, ResearchStatus


# ── Session CRUD ──────────────────────────────────────────────────────────────

def create_session(db: Session, user_id: str, topic: str) -> ResearchSession:
    try:
        session = ResearchSession(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            topic=topic,
            status=ResearchStatus.PENDING,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info("[research_service] Session created: {}", session.id)
        return session
    except Exception as exc:
        db.rollback()
        logger.error("[research_service] create_session failed: {}", exc)
        raise


def get_session(db: Session, session_id: str) -> ResearchSession | None:
    try:
        return (
            db.query(ResearchSession)
            .filter(ResearchSession.id == uuid.UUID(session_id))
            .first()
        )
    except Exception as exc:
        logger.error("[research_service] get_session failed: {}", exc)
        return None


def get_user_sessions(
    db: Session, user_id: str, limit: int = 20, offset: int = 0
) -> list[ResearchSession]:
    try:
        return (
            db.query(ResearchSession)
            .filter(ResearchSession.user_id == uuid.UUID(user_id))
            .order_by(ResearchSession.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    except Exception as exc:
        logger.error("[research_service] get_user_sessions failed: {}", exc)
        return []


def mark_running(db: Session, session_id: str) -> None:
    try:
        db.query(ResearchSession).filter(
            ResearchSession.id == uuid.UUID(session_id)
        ).update({"status": ResearchStatus.RUNNING})
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error("[research_service] mark_running failed: {}", exc)
        raise


def mark_completed(
    db: Session, session_id: str, report_json: dict[str, Any]
) -> None:
    try:
        db.query(ResearchSession).filter(
            ResearchSession.id == uuid.UUID(session_id)
        ).update(
            {
                "status": ResearchStatus.COMPLETED,
                "report_json": report_json,
            }
        )
        db.commit()
        logger.info("[research_service] Session completed: {}", session_id)
    except Exception as exc:
        db.rollback()
        logger.error("[research_service] mark_completed failed: {}", exc)
        raise


def mark_failed(db: Session, session_id: str, error: str) -> None:
    try:
        db.query(ResearchSession).filter(
            ResearchSession.id == uuid.UUID(session_id)
        ).update(
            {
                "status": ResearchStatus.FAILED,
                "error_message": error[:2000],
            }
        )
        db.commit()
        logger.warning("[research_service] Session failed: {} — {}", session_id, error[:120])
    except Exception as exc:
        db.rollback()
        logger.error("[research_service] mark_failed failed: {}", exc)
        raise


# ── Agent events ──────────────────────────────────────────────────────────────

def emit_event(
    db: Session,
    session_id: str,
    agent_name: str,
    event_type: str,
    payload: dict[str, Any] | None = None,
) -> AgentEvent:
    """
    Writes a single agent event row.
    Called at the start/end of each node so the frontend can poll for progress.
    """
    try:
        event = AgentEvent(
            id=uuid.uuid4(),
            session_id=uuid.UUID(session_id),
            agent_name=agent_name,
            event_type=event_type,
            payload=payload or {},
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        logger.debug(
            "[research_service] Event emitted: {} / {}", agent_name, event_type
        )
        return event
    except Exception as exc:
        db.rollback()
        logger.error("[research_service] emit_event failed: {}", exc)
        raise


def get_session_events(
    db: Session, session_id: str
) -> list[AgentEvent]:
    try:
        return (
            db.query(AgentEvent)
            .filter(AgentEvent.session_id == uuid.UUID(session_id))
            .order_by(AgentEvent.created_at.asc())
            .all()
        )
    except Exception as exc:
        logger.error("[research_service] get_session_events failed: {}", exc)
        return []


# ── Progress percentage ───────────────────────────────────────────────────────

_STATUS_PROGRESS: dict[str, int] = {
    "pending": 0,
    "searching": 25,
    "evaluating": 50,
    "synthesizing": 70,
    "writing": 85,
    "completed": 100,
    "failed": 0,
}

_EVENT_PROGRESS: dict[str, int] = {
    "planner_start": 5,
    "planner_end": 15,
    "searcher_start": 20,
    "searcher_end": 40,
    "evaluator_start": 45,
    "evaluator_end": 60,
    "synthesizer_start": 65,
    "synthesizer_end": 78,
    "writer_start": 82,
    "writer_end": 100,
}


def calculate_progress(session: ResearchSession) -> int:
    """
    Returns 0-100 progress pct.
    Prefers the most recent agent event's granular pct over the coarser status pct.
    """
    if session.agent_events:
        last_event = max(session.agent_events, key=lambda e: e.created_at)
        key = f"{last_event.agent_name}_{last_event.event_type}"
        if key in _EVENT_PROGRESS:
            return _EVENT_PROGRESS[key]
    return _STATUS_PROGRESS.get(session.status.value, 0)