"""
Searcher node — executes web searches and returns raw results.

Day 3: returns mock search results with the correct shape.
Day 4: replaces mock with real Tavily API calls + Redis caching + Pinecone storage.
"""
from datetime import date
from loguru import logger

from agents.state import ResearchState, SearchResult


async def searcher_node(state: ResearchState) -> dict:
    """
    Input:  state["search_queries"], state["search_iterations"]
    Output: raw_results (appended via reducer), status
    """
    queries = state["search_queries"]
    iteration = state["search_iterations"]
    logger.info(
        "[searcher] Iteration {} — running {} queries", iteration + 1, len(queries)
    )

    try:
        # ── Day 4 replaces this block with Tavily + Redis + Pinecone ──────
        today = str(date.today())
        raw_results: list[SearchResult] = []

        for i, query in enumerate(queries):
            raw_results.append(
                SearchResult(
                    query=query,
                    url=f"https://example-source-{i + 1}.com/article",
                    title=f"Research findings on: {query}",
                    content=(
                        f"This article covers {query} in depth. "
                        "Studies indicate significant developments in this area, "
                        "with researchers noting both promise and complexity. "
                        "Key contributors include academic institutions and industry labs."
                    ),
                    published_date=today,
                )
            )
        # ──────────────────────────────────────────────────────────────────

        logger.info("[searcher] Collected {} raw results", len(raw_results))

        return {
            "raw_results": raw_results,   # operator.add reducer appends these
            "status": "evaluating",
        }

    except Exception as exc:
        logger.error("[searcher] Failed: {}", exc)
        return {"error": str(exc), "status": "failed"}