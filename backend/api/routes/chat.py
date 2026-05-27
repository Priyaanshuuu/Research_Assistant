# REPLACE THIS FILE — 501 stub replaced with full RAG implementation

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session

from api.middleware.auth import TokenPayload, get_current_user
from api.schemas import ChatMessageOut, ChatRequest, ChatResponse
from db.database import get_db
from db.models import ChatMessage
from services import research_service
from services.rag_service import answer_question, get_chat_history

router = APIRouter(prefix="/chat", tags=["chat"])


def _to_out(msg: ChatMessage) -> ChatMessageOut:
    return ChatMessageOut(
        id=msg.id,
        session_id=msg.session_id,
        role=msg.role.value,
        content=msg.content,
        created_at=msg.created_at,
    )


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    req: ChatRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    """
    RAG-powered follow-up chat.

    Flow:
      validate session ownership → run RAG pipeline → return both messages
    """
    session = research_service.get_session(db, str(req.session_id))

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if str(session.user_id) != current_user.sub:
        raise HTTPException(status_code=403, detail="Not your session")
    if session.status.value != "completed":
        raise HTTPException(
            status_code=400,
            detail="Research must be completed before chatting",
        )

    try:
        user_msg, assistant_msg = await answer_question(
            db=db,
            session_id=str(req.session_id),
            topic=session.topic,
            question=req.message.strip(),
        )

        logger.info(
            "[chat] Answered question for session {} user {}",
            str(req.session_id)[:8],
            current_user.email,
        )

        return ChatResponse(
            user_message=_to_out(user_msg),
            assistant_message=_to_out(assistant_msg),
        )

    except Exception as exc:
        logger.error("[chat] Failed: {}", exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate answer. Please try again.",
        )


@router.get("/history/{session_id}", response_model=list[ChatMessageOut])
async def get_history(
    session_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatMessageOut]:
    """Returns full conversation history for a session."""
    session = research_service.get_session(db, session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if str(session.user_id) != current_user.sub:
        raise HTTPException(status_code=403, detail="Not your session")

    messages = await get_chat_history(db, session_id)
    return [_to_out(m) for m in messages]