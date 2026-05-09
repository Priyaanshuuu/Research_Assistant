"""
Evaluator node — scores search results for credibility and relevance,
then decides whether another search iteration is needed.

Day 3: assigns mock scores and always routes to synthesizer.
Day 5: replaces mock scoring with GPT-4o-mini structured output + token budget guard.
"""
from loguru import logger

from agents.state import EvaluatedResult, ResearchState

# Maximum search/evaluate cycles before forcing synthesis
MAX_ITERATIONS = 3

# Minimum average combined score before we accept results
QUALITY_THRESHOLD = 0.60


async def evaluator_node(state: ResearchState) -> dict:
    """
    Input:  state["raw_results"], state["search_iterations"]
    Output: evaluated_results (appended via reducer), needs_more_search,
            search_iterations (incremented), status
    """
    raw = state["raw_results"]
    iteration = state["search_iterations"]
    logger.info("[evaluator] Scoring {} raw results (iteration {})", len(raw), iteration + 1)

    try:
        # ── Day 5 replaces this block with GPT-4o-mini scoring ────────────
        evaluated: list[EvaluatedResult] = []

        for i, result in enumerate(raw):
            # Mock scores that vary slightly so the output looks realistic
            credibility = round(0.75 + (i % 3) * 0.05, 2)
            relevance = round(0.80 + (i % 4) * 0.04, 2)
            combined = round((credibility * 0.4) + (relevance * 0.6), 2)

            evaluated.append(
                EvaluatedResult(
                    query=result["query"],
                    url=result["url"],
                    title=result["title"],
                    content=result["content"],
                    published_date=result.get("published_date"),
                    credibility_score=credibility,
                    relevance_score=relevance,
                    combined_score=combined,
                )
            )

        avg_score = sum(r["combined_score"] for r in evaluated) / max(len(evaluated), 1)
        new_iteration = iteration + 1

        # Decide whether we need another search pass
        needs_more = (
            avg_score < QUALITY_THRESHOLD
            and new_iteration < MAX_ITERATIONS
        )
        # ──────────────────────────────────────────────────────────────────

        logger.info(
            "[evaluator] Avg score: {:.2f} | needs_more_search: {} | iteration: {}",
            avg_score,
            needs_more,
            new_iteration,
        )

        return {
            "evaluated_results": evaluated,   # operator.add reducer appends
            "needs_more_search": needs_more,
            "search_iterations": new_iteration,
            "status": "searching" if needs_more else "synthesizing",
        }

    except Exception as exc:
        logger.error("[evaluator] Failed: {}", exc)
        return {"error": str(exc), "status": "failed"}


def routing_decision(state: ResearchState) -> str:
    """
    Conditional edge function — called by LangGraph after evaluator_node.
    Returns the name of the next node to execute.
    """
    if state.get("needs_more_search") and state["search_iterations"] < MAX_ITERATIONS:
        logger.info("[router] Routing back to searcher for iteration {}", state["search_iterations"] + 1)
        return "searcher"

    logger.info("[router] Quality threshold met — routing to synthesizer")
    return "synthesizer"