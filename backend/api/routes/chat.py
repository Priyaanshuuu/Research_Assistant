from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.middleware.auth import TokenPayload, get_current_user
from api.schemas import ChatRequest, ChatResponse
from db.database import get_db
from services import research_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    req: ChatRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    """
    RAG-powered follow-up chat.
    Stub until Day 8 — returns 501 so the frontend knows it's not ready.
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

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Chat is not implemented yet — coming in Day 8",
    )