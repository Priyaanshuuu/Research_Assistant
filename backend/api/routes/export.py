import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from loguru import logger
from sqlalchemy.orm import Session

from api.middleware.auth import TokenPayload, get_current_user
from db.database import get_db
from services import research_service
from services.export_service import generate_markdown, generate_pdf

router = APIRouter(prefix="/export", tags=["export"])


def _safe_filename(title: str) -> str:
    """Converts report title into a filesystem-safe ASCII filename."""
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-")
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"research-report-{slug[:40]}-{date_str}"


@router.get("/{session_id}")
async def export_report(
    session_id: str,
    format: str = Query(default="pdf", pattern="^(pdf|markdown)$"),
    current_user: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """
    Streams the research report as a downloadable file.

    Query params:
      format=pdf       → application/pdf
      format=markdown  → text/markdown
    """
    session = research_service.get_session(db, session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if str(session.user_id) != current_user.sub:
        raise HTTPException(status_code=403, detail="Not your session")
    if session.status.value != "completed":
        raise HTTPException(
            status_code=400,
            detail="Report is not ready yet — research must be completed",
        )
    if not session.report_json:
        raise HTTPException(status_code=404, detail="Report data not found")

    report: dict = session.report_json
    filename = _safe_filename(report.get("title", "research-report"))

    try:
        if format == "pdf":
            logger.info("[export] Generating PDF for session {}", session_id[:8])
            content = generate_pdf(report)
            return Response(
                content=content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}.pdf"',
                    "Content-Length": str(len(content)),
                },
            )

        # Markdown
        logger.info("[export] Generating Markdown for session {}", session_id[:8])
        content = generate_markdown(report)
        return Response(
            content=content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}.md"',
                "Content-Length": str(len(content)),
            },
        )

    except Exception as exc:
        logger.error("[export] Generation failed: {}", exc)
        raise HTTPException(status_code=500, detail="Export generation failed")