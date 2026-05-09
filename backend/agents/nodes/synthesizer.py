"""
Synthesizer node — merges all evaluated results into a coherent synthesis
that the Writer node will structure into the final report.

Day 3: returns a mock synthesis string.
Day 5: replaces mock with a GPT-4o summarisation chain over all evaluated results.
"""
from loguru import logger

from agents.state import ResearchState


async def synthesizer_node(state: ResearchState) -> dict:
    """
    Input:  state["evaluated_results"], state["sub_questions"], state["topic"]
    Output: synthesis, status
    """
    results = state["evaluated_results"]
    topic = state["topic"]
    sub_questions = state["sub_questions"]

    logger.info(
        "[synthesizer] Synthesising {} evaluated results for topic: '{}'",
        len(results),
        topic,
    )

    try:
        # ── Day 5 replaces this block with GPT-4o summarisation ───────────
        top_results = sorted(results, key=lambda r: r["combined_score"], reverse=True)[:5]

        synthesis_parts = [
            f"Research synthesis on: {topic}",
            "",
            "Key findings:",
        ]

        for i, sq in enumerate(sub_questions, 1):
            synthesis_parts.append(f"\n{i}. {sq}")
            if i <= len(top_results):
                synthesis_parts.append(f"   → {top_results[i - 1]['content'][:200]}...")

        synthesis_parts += [
            "",
            f"Sources reviewed: {len(results)}",
            f"Average quality score: {sum(r['combined_score'] for r in results) / max(len(results), 1):.2f}",
        ]

        synthesis = "\n".join(synthesis_parts)
        # ──────────────────────────────────────────────────────────────────

        logger.info("[synthesizer] Synthesis complete ({} chars)", len(synthesis))

        return {
            "synthesis": synthesis,
            "status": "writing",
        }

    except Exception as exc:
        logger.error("[synthesizer] Failed: {}", exc)
        return {"error": str(exc), "status": "failed"}