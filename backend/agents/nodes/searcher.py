from loguru import logger

from agents.state import ResearchState, SearchResult
from services.pinecone_service import upsert_search_results
from services.redis_service import get_cached_results, set_cached_results
from tools.web_search import tavily_search


async def searcher_node(state: ResearchState) -> dict:
    """
    Input:  state["search_queries"], state["search_iterations"], state["session_id"]
    Output: raw_results (appended via operator.add reducer), status

    Pipeline per query:
        Redis cache hit  → use cached results (no Tavily call, no Pinecone upsert)
        Redis cache miss → Tavily search → cache in Redis → embed + upsert to Pinecone
    """
    queries: list[str] = state["search_queries"]
    iteration: int = state["search_iterations"]
    session_id: str = state["session_id"]

    logger.info(
        "[searcher] Iteration {} — {} queries for session {}",
        iteration + 1,
        len(queries),
        session_id[:8],
    )

    try:
        fresh_results: list[SearchResult] = []  
        cached_results: list[SearchResult] = [] 
        
        cache_hits = 0

        for query in queries:
            # ── 1. Redis cache check ──────────────────────────────────────
            cached = await get_cached_results(query)

            if cached is not None:
                cache_hits += 1
                cached_results.extend(cached)  
                continue

            # ── 2. Cache miss → Tavily ────────────────────────────────────
            results = await tavily_search(query, max_results=5)

            if results:
                # ── 3. Store in Redis (24-hour TTL) ───────────────────────
                await set_cached_results(query, list(results))
                fresh_results.extend(results)

        # ── 4. Embed fresh results → Pinecone ────────────────────────────
        if fresh_results:
            upserted = await upsert_search_results(session_id, list(fresh_results))
            logger.info("[searcher] Upserted {} vectors to Pinecone", upserted)

        all_results = fresh_results + cached_results

        logger.info(
            "[searcher] {} total results | {} from Tavily | {} from cache",
            len(all_results),
            len(fresh_results),
            cache_hits,
        )

        return {
            "raw_results": all_results,
            "status": "evaluating",
        }

    except Exception as exc:
        logger.error("[searcher] Failed: {}", exc)
        return {"error": str(exc), "status": "failed"}