"""
Planner node — decomposes a research topic into sub-questions and search queries.

Day 3: returns structured mock data with the correct shape.
Day 4: replaces mock with GPT-4o structured output call.
"""
from loguru import logger

from agents.state import ResearchState


async def planner_node(state: ResearchState) -> dict:
    """
    Input:  state["topic"]
    Output: sub_questions, search_queries, status
    """
    topic = state["topic"]
    logger.info("[planner] Starting — topic: '{}'", topic)

    try:
        # ── Day 4 replaces this block with a real GPT-4o call ─────────────
        sub_questions = [
            f"What are the core concepts behind {topic}?",
            f"What is the current state of research on {topic}?",
            f"What are the key challenges and limitations of {topic}?",
            f"What are real-world applications of {topic}?",
            f"What does the future outlook for {topic} look like?",
        ]

        search_queries = [
            f"{topic} overview 2024",
            f"{topic} latest research findings",
            f"{topic} challenges limitations",
            f"{topic} real world applications",
            f"{topic} future trends",
        ]
        # ──────────────────────────────────────────────────────────────────

        logger.info(
            "[planner] Generated {} sub-questions and {} search queries",
            len(sub_questions),
            len(search_queries),
        )

        return {
            "sub_questions": sub_questions,
            "search_queries": search_queries,
            "status": "searching",
        }

    except Exception as exc:
        logger.error("[planner] Failed: {}", exc)
        return {"error": str(exc), "status": "failed"}