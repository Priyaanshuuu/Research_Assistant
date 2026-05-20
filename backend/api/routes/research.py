import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy.orm import Session

from agents.graph import get_research_graph
from agents.state import ResearchState
from api.middleware.auth import TokenPayload, get_current_user
from api.schemas import (
    ResearchSessionOut,
    ResearchStatusResponse,
    StartResearchRequest,
    StartResearchResponse,
)
from db.database import SessionLocal, get_db
from db.models import ResearchSession
from services import research_service

router = APIRouter(prefix="/research", tags=["research"])


# ── Background task ───────────────────────────────────────────────────────────

async def _run_research(session_id: str, user_id: str, topic: str) -> None:
    """
    Runs the full LangGraph pipeline in the background.
    Uses its own DB session (not the request session — that's already closed).
    Emits AgentEvent rows before and after each node for the progress board.
    """
    db: Session = SessionLocal()

    try:
        research_service.mark_running(db, session_id)
        research_service.emit_event(db, session_id, "planner", "start")

        initial_state: ResearchState = {
            "session_id": session_id,
            "user_id": user_id,
            "topic": topic,
            "sub_questions": [],
            "search_queries": [],
            "raw_results": [],
            "evaluated_results": [],
            "needs_more_search": False,
            "search_iterations": 0,
            "synthesis": "",
            "report": {},  # type: ignore[typeddict-item]
            "status": "pending",
            "error": None,
        }

        thread_id = f"session-{session_id[:8]}"
        run_config = {"configurable": {"thread_id": thread_id}}

        async with get_research_graph() as graph:
            # Stream node-by-node so we can emit progress events in real time
            async for chunk in graph.astream(
                initial_state, config=run_config, stream_mode="updates"
            ):
                for node_name, node_output in chunk.items():
                    _handle_node_event(db, session_id, node_name, node_output)

        # Re-fetch final state from checkpointer via a second invocation
        # (astream gives us deltas; we need the final merged state for the report)
        async with get_research_graph() as graph:
            final_state = await graph.aget_state(run_config)
            values: dict[str, Any] = final_state.values

        if values.get("error"):
            research_service.mark_failed(db, session_id, values["error"])
        else:
            research_service.mark_completed(db, session_id, values["report"])

    except Exception as exc:
        logger.error("[research_bg] Session {} failed: {}", session_id, exc)
        try:
            research_service.mark_failed(db, session_id, str(exc))
        except Exception:
            pass
    finally:
        db.close()


def _handle_node_event(
    db: Session,
    session_id: str,
    node_name: str,
    output: dict[str, Any],
) -> None:
    """Emits a structured AgentEvent row for each completed node."""
    try:
        payload: dict[str, Any] = {"status": output.get("status", "")}

        if node_name == "planner":
            payload["sub_questions_count"] = len(output.get("sub_questions", []))
            payload["search_queries_count"] = len(output.get("search_queries", []))
            research_service.emit_event(db, session_id, "planner", "end", payload)

        elif node_name == "searcher":
            payload["results_count"] = len(output.get("raw_results", []))
            research_service.emit_event(db, session_id, "searcher", "end", payload)

        elif node_name == "evaluator":
            payload["evaluated_count"] = len(output.get("evaluated_results", []))
            payload["needs_more_search"] = output.get("needs_more_search", False)
            research_service.emit_event(db, session_id, "evaluator", "end", payload)

        elif node_name == "synthesizer":
            payload["synthesis_length"] = len(output.get("synthesis", ""))
            research_service.emit_event(db, session_id, "synthesizer", "end", payload)

        elif node_name == "writer":
            report = output.get("report", {})
            payload["sections_count"] = len(report.get("sections", []))
            payload["citations_count"] = len(report.get("all_citations", []))
            research_service.emit_event(db, session_id, "writer", "end", payload)

    except Exception as exc:
        logger.warning("[research_bg] emit_event failed for node {}: {}", node_name, exc)


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post(
    "/start",
    response_model=StartResearchResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_research(
    req: StartResearchRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StartResearchResponse:
    """Creates a session and immediately returns — graph runs in the background."""
    try:
        session = research_service.create_session(db, current_user.sub, req.topic)

        background_tasks.add_task(
            _run_research,
            str(session.id),
            current_user.sub,
            req.topic,
        )

        logger.info(
            "[research] Session {} started for user {}", session.id, current_user.email
        )

        return StartResearchResponse(
            session_id=session.id,
            status="pending",
            message="Research started. Poll /research/status/{id} for progress.",
        )
    except Exception as exc:
        logger.error("[research] start_research failed: {}", exc)
        raise HTTPException(status_code=500, detail="Failed to start research session")


@router.get("/status/{session_id}", response_model=ResearchStatusResponse)
async def get_research_status(
    session_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchStatusResponse:
    """Lightweight polling endpoint — called every 3 seconds by the progress board."""
    session = research_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if str(session.user_id) != current_user.sub:
        raise HTTPException(status_code=403, detail="Not your session")

    events = research_service.get_session_events(db, session_id)
    session.agent_events = events

    latest_event: str | None = None
    if events:
        last = events[-1]
        latest_event = f"{last.agent_name}: {last.event_type}"

    return ResearchStatusResponse(
        session_id=session.id,
        status=session.status.value,
        progress_pct=research_service.calculate_progress(session),
        latest_event=latest_event,
        error_message=session.error_message,
    )


@router.get("/{session_id}", response_model=ResearchSessionOut)
async def get_research_session(
    session_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchSession:
    """Returns the full session including report_json and all agent events."""
    session = research_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if str(session.user_id) != current_user.sub:
        raise HTTPException(status_code=403, detail="Not your session")

    session.agent_events = research_service.get_session_events(db, session_id)
    return session


@router.get("/", response_model=list[ResearchSessionOut])
async def list_research_sessions(
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ResearchSession]:
    """Returns paginated list of all sessions for the current user."""
    return research_service.get_user_sessions(
        db, current_user.sub, limit=limit, offset=offset
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_research_session(
    session_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Deletes a session and all its child rows (cascade)."""
    session = research_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if str(session.user_id) != current_user.sub:
        raise HTTPException(status_code=403, detail="Not your session")
    try:
        db.delete(session)
        db.commit()
        logger.info("[research] Session {} deleted", session_id)
    except Exception as exc:
        db.rollback()
        logger.error("[research] delete failed: {}", exc)
        raise HTTPException(status_code=500, detail="Delete failed")