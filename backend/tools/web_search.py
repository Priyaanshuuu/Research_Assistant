"""
Tavily web search wrapper.
Returns typed SearchResult dicts ready for the Searcher node.
"""
import asyncio
from functools import lru_cache

from loguru import logger
from tavily import TavilyClient

from agents.state import SearchResult
from core.config import settings


@lru_cache(maxsize=1)
def _get_client() -> TavilyClient:
    return TavilyClient(api_key=settings.TAVILY_API_KEY)


async def tavily_search(query: str, max_results: int = 5) -> list[SearchResult]:
    """
    Searches the web via Tavily and returns structured SearchResult objects.
    The Tavily client is synchronous — executed in a thread-pool executor
    so it doesn't block the event loop.
    """
    try:
        client = _get_client()
        loop = asyncio.get_event_loop()

        response: dict = await loop.run_in_executor(
            None,
            lambda: client.search(
                query=query,
                max_results=max_results,
                include_raw_content=False,
                search_depth="advanced",
            ),
        )

        results: list[SearchResult] = []
        for r in response.get("results", []):
            url = r.get("url", "").strip()
            content = r.get("content", "").strip()
            if not url or not content:
                continue

            results.append(
                SearchResult(
                    query=query,
                    url=url,
                    title=r.get("title", "").strip(),
                    content=content,
                    published_date=r.get("published_date"),
                )
            )

        logger.info(
            "[web_search] '{}' → {} results", query[:60], len(results)
        )
        return results

    except Exception as exc:
        logger.error("[web_search] Tavily failed for '{}': {}", query[:60], exc)
        return []