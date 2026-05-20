from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.middleware.auth import TokenPayload, get_current_user
from api.schemas import ExportRequest
from db.database import get_db
from services import research_service

router = APIRouter(prefix="/export", tags=["export"])


@router.post("/")
async def export_report(
    req: ExportRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    PDF / Markdown export.
    Stub until Day 9 — returns 501.
    """
    session = research_service.get_session(db, str(req.session_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if str(session.user_id) != current_user.sub:
        raise HTTPException(status_code=403, detail="Not your session")

    raise HTTPException(
        status_code=501,
        detail="Export not implemented yet — coming in Day 9",
    )