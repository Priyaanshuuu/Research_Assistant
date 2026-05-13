# REPLACE THIS FILE — mock replaced with GPT-4o structured output

from datetime import datetime, timezone

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import BaseModel, Field

from agents.state import EvaluatedResult, ResearchReport, ResearchState
from core.config import settings


# ── Pydantic schemas for GPT-4o structured output ────────────────────────────

class ReportSectionOutput(BaseModel):
    heading: str = Field(description="Clear, descriptive section heading")
    body: str = Field(
        description=(
            "2-4 paragraph section body in polished academic prose. "
            "Cite sources inline using [Source Title] notation."
        )
    )
    citations: list[str] = Field(
        description="List of URLs referenced in this section body"
    )


class ReportOutput(BaseModel):
    title: str = Field(description="Engaging, descriptive report title")
    summary: str = Field(
        description=(
            "Executive summary of the entire report in 3-5 sentences. "
            "Highlight the most important findings and their implications."
        )
    )
    sections: list[ReportSectionOutput] = Field(
        description=(
            "One section per sub-question, in the same order as the sub-questions. "
            "Each section must be substantive — minimum 150 words."
        )
    )
    key_takeaways: list[str] = Field(
        description="3-5 concise bullet-point takeaways distilled from the full report"
    )


_WRITER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert research writer producing a structured, \
publication-quality research report.

Guidelines:
- Write in clear, authoritative, academic prose
- Each section must directly answer its sub-question using the synthesis
- Cite sources inline as [Source Title] and include the URL in the citations list
- The summary must stand alone as an executive overview
- Key takeaways must be actionable and specific — avoid generic statements
- Do not fabricate information — only use what is in the synthesis and sources""",
        ),
        (
            "human",
            """Research topic: {topic}

Sub-questions (one section per question, in order):
{sub_questions}

Research synthesis:
{synthesis}

Available sources (use URLs in citations):
{sources_list}

Generate the complete structured report now:""",
        ),
    ]
)


def _format_sources_list(results: list[EvaluatedResult]) -> str:
    """Compact source list for the writer prompt."""
    seen_urls: set[str] = set()
    lines: list[str] = []
    for r in sorted(results, key=lambda x: x["combined_score"], reverse=True):
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            lines.append(f"- [{r['title']}]({r['url']}) — score: {r['combined_score']:.2f}")
    return "\n".join(lines)


async def writer_node(state: ResearchState) -> dict:
    """
    Input:  state["synthesis"], state["evaluated_results"],
            state["topic"], state["sub_questions"]
    Output: report (ResearchReport TypedDict), status
    """
    synthesis = state["synthesis"]
    topic = state["topic"]
    evaluated = state["evaluated_results"]
    sub_questions = state["sub_questions"]

    logger.info("[writer] Building structured report for '{}'", topic)

    try:
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.2,
            openai_api_key=settings.OPENAI_API_KEY,
        )

        chain = _WRITER_PROMPT | llm.with_structured_output(ReportOutput)

        sub_q_formatted = "\n".join(
            f"{i}. {q}" for i, q in enumerate(sub_questions, 1)
        )

        result: ReportOutput = await chain.ainvoke(
            {
                "topic": topic,
                "sub_questions": sub_q_formatted,
                "synthesis": synthesis,
                "sources_list": _format_sources_list(evaluated),
            }
        )

        # ── Deduplicate and order all citations ───────────────────────────
        seen: set[str] = set()
        all_citations: list[str] = []
        for section in result.sections:
            for url in section.citations:
                if url and url not in seen:
                    seen.add(url)
                    all_citations.append(url)

        # ── Build final ResearchReport TypedDict ──────────────────────────
        report = ResearchReport(
            title=result.title,
            summary=result.summary,
            sections=[
                {
                    "heading": s.heading,
                    "body": s.body,
                    "citations": s.citations,
                }
                for s in result.sections
            ],
            all_citations=all_citations,
            topic=topic,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

        logger.info(
            "[writer] Report complete — '{}' | {} sections | {} citations",
            report["title"],
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