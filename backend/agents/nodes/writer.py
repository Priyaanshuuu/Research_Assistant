"""
Writer node — converts the synthesis into a structured ResearchReport JSON.

Day 3: returns a mock report with the correct schema.
Day 5: replaces mock with a GPT-4o structured-output call that produces
       properly cited, section-by-section report content.
"""
from datetime import datetime, timezone
from loguru import logger

from agents.state import ResearchReport, ResearchState


async def writer_node(state: ResearchState) -> dict:
    """
    Input:  state["synthesis"], state["evaluated_results"], state["topic"]
    Output: report (ResearchReport), status
    """
    synthesis = state["synthesis"]
    topic = state["topic"]
    evaluated = state["evaluated_results"]
    sub_questions = state["sub_questions"]

    logger.info("[writer] Building report for topic: '{}'", topic)

    try:
        # ── Day 5 replaces this block with GPT-4o structured output ───────
        # Deduplicate citation URLs, sorted by score descending
        top_sources = sorted(evaluated, key=lambda r: r["combined_score"], reverse=True)
        all_citations = list(dict.fromkeys(r["url"] for r in top_sources))

        sections = []
        for i, sq in enumerate(sub_questions):
            source_url = all_citations[i] if i < len(all_citations) else ""
            sections.append(
                {
                    "heading": sq,
                    "body": (
                        f"Analysis of '{sq}': Based on the gathered research, "
                        f"this area demonstrates significant activity and evolving understanding. "
                        f"Multiple sources confirm the importance of this dimension "
                        f"within the broader context of {topic}."
                    ),
                    "citations": [source_url] if source_url else [],
                }
            )

        report = ResearchReport(
            title=f"Research Report: {topic}",
            summary=(
                f"This report examines {topic} across {len(sub_questions)} key dimensions, "
                f"drawing on {len(evaluated)} evaluated sources. "
                f"The findings highlight both the current state of knowledge and "
                f"emerging directions in this field."
            ),
            sections=sections,
            all_citations=all_citations,
            topic=topic,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
        # ──────────────────────────────────────────────────────────────────

        logger.info(
            "[writer] Report complete — {} sections, {} citations",
            len(report["sections"]),
            len(report["all_citations"]),
        )

        return {
            "report": report,
            "status": "completed",
        }

    except Exception as exc:
        logger.error("[writer] Failed: {}", exc)
        return {"error": str(exc), "status": "failed"}