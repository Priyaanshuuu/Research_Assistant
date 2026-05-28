"""
Export service — generates PDF and Markdown from a ResearchReport dict.
PDF is built with ReportLab; Markdown is pure string construction.
Both return raw bytes ready to stream as a FileResponse.
"""
import io
import textwrap
from datetime import datetime, timezone

from loguru import logger
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ── Colour palette (matches the violet/slate frontend theme) ──────────────────
VIOLET = colors.HexColor("#7c3aed")
SLATE_900 = colors.HexColor("#0f172a")
SLATE_600 = colors.HexColor("#475569")
SLATE_200 = colors.HexColor("#e2e8f0")
AMBER_50 = colors.HexColor("#fffbeb")
AMBER_700 = colors.HexColor("#b45309")
VIOLET_50 = colors.HexColor("#f5f3ff")


# ── PDF builder ───────────────────────────────────────────────────────────────

def _build_styles() -> dict:
    base = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontSize=22,
            textColor=SLATE_900,
            spaceAfter=6,
            fontName="Helvetica-Bold",
        ),
        "meta": ParagraphStyle(
            "Meta",
            parent=base["Normal"],
            fontSize=9,
            textColor=SLATE_600,
            spaceAfter=20,
        ),
        "section_label": ParagraphStyle(
            "SectionLabel",
            parent=base["Normal"],
            fontSize=8,
            textColor=VIOLET,
            spaceBefore=18,
            spaceAfter=4,
            fontName="Helvetica-Bold",
            textTransform="uppercase",
        ),
        "summary_body": ParagraphStyle(
            "SummaryBody",
            parent=base["Normal"],
            fontSize=10,
            textColor=SLATE_900,
            leading=15,
            spaceAfter=6,
        ),
        "heading": ParagraphStyle(
            "SectionHeading",
            parent=base["Heading2"],
            fontSize=13,
            textColor=SLATE_900,
            fontName="Helvetica-Bold",
            spaceBefore=20,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "SectionBody",
            parent=base["Normal"],
            fontSize=10,
            textColor=SLATE_600,
            leading=15,
            spaceAfter=8,
        ),
        "takeaway": ParagraphStyle(
            "Takeaway",
            parent=base["Normal"],
            fontSize=10,
            textColor=AMBER_700,
            leading=14,
            leftIndent=12,
            spaceAfter=4,
        ),
        "citation": ParagraphStyle(
            "Citation",
            parent=base["Normal"],
            fontSize=8,
            textColor=SLATE_600,
            leading=12,
            leftIndent=12,
        ),
    }


def _header_footer(canvas, doc) -> None:
    """Draws page number footer on every page."""
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(SLATE_600)
    canvas.drawRightString(
        A4[0] - 2 * cm,
        1.2 * cm,
        f"Page {doc.page}",
    )
    canvas.drawString(2 * cm, 1.2 * cm, "Research Assistant — AI-Generated Report")
    canvas.restoreState()


def generate_pdf(report: dict) -> bytes:
    """
    Converts a ResearchReport dict into a PDF and returns raw bytes.
    Raises on any ReportLab error.
    """
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        title=report.get("title", "Research Report"),
        author="Research Assistant",
    )

    styles = _build_styles()
    story = []

    # ── Title ─────────────────────────────────────────────────────────────
    story.append(Paragraph(report.get("title", "Research Report"), styles["title"]))

    generated_at = report.get("generated_at", "")
    if generated_at:
        try:
            dt = datetime.fromisoformat(generated_at)
            generated_at = dt.strftime("%B %d, %Y at %H:%M UTC")
        except ValueError:
            pass

    story.append(
        Paragraph(
            f"Generated {generated_at} · Topic: {report.get('topic', '')}",
            styles["meta"],
        )
    )
    story.append(HRFlowable(width="100%", thickness=1, color=SLATE_200, spaceAfter=16))

    # ── Executive summary ──────────────────────────────────────────────────
    story.append(Paragraph("Executive Summary", styles["section_label"]))
    story.append(Paragraph(report.get("summary", ""), styles["summary_body"]))
    story.append(Spacer(1, 12))

    # ── Key takeaways ──────────────────────────────────────────────────────
    takeaways = report.get("key_takeaways", [])
    if takeaways:
        story.append(Paragraph("Key Takeaways", styles["section_label"]))
        for i, t in enumerate(takeaways, 1):
            story.append(Paragraph(f"{i}.  {t}", styles["takeaway"]))
        story.append(Spacer(1, 12))

    story.append(HRFlowable(width="100%", thickness=0.5, color=SLATE_200, spaceAfter=12))

    # ── Sections ───────────────────────────────────────────────────────────
    sections = report.get("sections", [])
    for i, section in enumerate(sections, 1):
        story.append(
            Paragraph(f"{i}. {section.get('heading', '')}", styles["heading"])
        )

        body_text = section.get("body", "")
        # Split on double newline to preserve paragraph breaks from GPT output
        for para in body_text.split("\n\n"):
            para = para.strip()
            if para:
                story.append(Paragraph(para, styles["body"]))

        citations = section.get("citations", [])
        if citations:
            story.append(Spacer(1, 4))
            for url in citations:
                story.append(Paragraph(f"↗  {url}", styles["citation"]))

        story.append(Spacer(1, 8))

    # ── All citations ──────────────────────────────────────────────────────
    all_citations = report.get("all_citations", [])
    if all_citations:
        story.append(PageBreak())
        story.append(Paragraph("All Citations", styles["section_label"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=SLATE_200, spaceAfter=8))
        for i, url in enumerate(all_citations, 1):
            story.append(Paragraph(f"[{i}]  {url}", styles["citation"]))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return buf.getvalue()


# ── Markdown builder ──────────────────────────────────────────────────────────

def generate_markdown(report: dict) -> bytes:
    """
    Converts a ResearchReport dict into a Markdown string and returns UTF-8 bytes.
    """
    lines: list[str] = []

    title = report.get("title", "Research Report")
    topic = report.get("topic", "")
    generated_at = report.get("generated_at", "")
    summary = report.get("summary", "")
    takeaways: list[str] = report.get("key_takeaways", [])
    sections: list[dict] = report.get("sections", [])
    all_citations: list[str] = report.get("all_citations", [])

    # Title block
    lines += [
        f"# {title}",
        "",
        f"**Topic:** {topic}  ",
        f"**Generated:** {generated_at}",
        "",
        "---",
        "",
    ]

    # Summary
    lines += [
        "## Executive Summary",
        "",
        summary,
        "",
    ]

    # Key takeaways
    if takeaways:
        lines += ["## Key Takeaways", ""]
        for i, t in enumerate(takeaways, 1):
            lines.append(f"{i}. {t}")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Sections
    for i, section in enumerate(sections, 1):
        heading = section.get("heading", "")
        body = section.get("body", "")
        citations: list[str] = section.get("citations", [])

        lines += [f"## {i}. {heading}", "", body, ""]

        if citations:
            lines.append("**Sources:**")
            for url in citations:
                lines.append(f"- {url}")
            lines.append("")

    # All citations
    if all_citations:
        lines += ["---", "", "## All Citations", ""]
        for i, url in enumerate(all_citations, 1):
            lines.append(f"[{i}] {url}")

    return "\n".join(lines).encode("utf-8")