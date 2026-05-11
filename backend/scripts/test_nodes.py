"""
Isolated node tester — tests Planner and Searcher individually
without running the full graph, so you can diagnose API issues quickly.

Usage:
    python scripts/test_nodes.py planner
    python scripts/test_nodes.py searcher
    python scripts/test_nodes.py both
"""
import asyncio
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger


# ── Planner test ──────────────────────────────────────────────────────────────

async def test_planner(topic: str) -> dict:
    from agents.nodes.planner import planner_node

    print(f"\n{'='*60}")
    print(f"TESTING PLANNER — topic: '{topic}'")
    print("=" * 60)

    state = {
        "session_id": str(uuid.uuid4()),
        "user_id": "test-user",
        "topic": topic,
        "sub_questions": [],
        "search_queries": [],
        "raw_results": [],
        "evaluated_results": [],
        "needs_more_search": False,
        "search_iterations": 0,
        "synthesis": "",
        "report": {},
        "status": "pending",
        "error": None,
    }

    result = await planner_node(state)

    if result.get("error"):
        print(f"❌  Planner error: {result['error']}")
        return result

    print(f"\n✅  Sub-questions ({len(result['sub_questions'])}):")
    for i, q in enumerate(result["sub_questions"], 1):
        print(f"   {i}. {q}")

    print(f"\n✅  Search queries ({len(result['search_queries'])}):")
    for i, q in enumerate(result["search_queries"], 1):
        print(f"   {i}. {q}")

    return result


# ── Searcher test ─────────────────────────────────────────────────────────────

async def test_searcher(search_queries: list[str]) -> dict:
    from agents.nodes.searcher import searcher_node

    session_id = str(uuid.uuid4())
    print(f"\n{'='*60}")
    print(f"TESTING SEARCHER — {len(search_queries)} queries | session: {session_id[:8]}")
    print("=" * 60)

    state = {
        "session_id": session_id,
        "user_id": "test-user",
        "topic": "test topic",
        "sub_questions": [],
        "search_queries": search_queries,
        "raw_results": [],
        "evaluated_results": [],
        "needs_more_search": False,
        "search_iterations": 0,
        "synthesis": "",
        "report": {},
        "status": "searching",
        "error": None,
    }

    result = await searcher_node(state)

    if result.get("error"):
        print(f"❌  Searcher error: {result['error']}")
        return result

    raw = result.get("raw_results", [])
    print(f"\n✅  {len(raw)} results collected")

    for i, r in enumerate(raw[:3], 1):   # show first 3
        print(f"\n   [{i}] {r['title']}")
        print(f"       URL  : {r['url']}")
        print(f"       Chars: {len(r['content'])}")
        print(f"       Date : {r.get('published_date', 'N/A')}")

    return {"raw_results": raw, "session_id": session_id}


# ── Redis cache verification ──────────────────────────────────────────────────

async def verify_redis_cache(query: str) -> None:
    from services.redis_service import get_cached_results

    print(f"\n{'='*60}")
    print("VERIFYING REDIS CACHE")
    print("=" * 60)

    cached = await get_cached_results(query)
    if cached:
        print(f"✅  Cache HIT — {len(cached)} results stored for query: '{query[:60]}'")
    else:
        print(f"❌  Cache MISS — no results cached for: '{query[:60]}'")


# ── Pinecone verification ─────────────────────────────────────────────────────

async def verify_pinecone(session_id: str, query: str) -> None:
    from services.pinecone_service import query_similar

    print(f"\n{'='*60}")
    print(f"VERIFYING PINECONE — session: {session_id[:8]}")
    print("=" * 60)

    matches = await query_similar(session_id, query, top_k=3)
    if matches:
        print(f"✅  Pinecone returned {len(matches)} matches:")
        for i, m in enumerate(matches, 1):
            print(f"   [{i}] score={m['score']} | {m['title'][:60]}")
            print(f"       {m['content'][:120]}...")
    else:
        print("❌  No Pinecone matches found — check index name and API key")


# ── Entry point ───────────────────────────────────────────────────────────────

async def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"
    topic = "Retrieval-Augmented Generation in enterprise AI systems"

    planner_result: dict = {}
    searcher_result: dict = {}

    if mode in ("planner", "both"):
        planner_result = await test_planner(topic)

    if mode in ("searcher", "both"):
        queries = planner_result.get(
            "search_queries",
            [
                "retrieval augmented generation enterprise 2024",
                "RAG vs fine-tuning LLM production comparison",
            ],
        )
        searcher_result = await test_searcher(queries)

        if searcher_result.get("raw_results"):
            first_query = queries[0]
            await verify_redis_cache(first_query)

            session_id = searcher_result.get("session_id", "")
            if session_id:
                await verify_pinecone(session_id, topic)


if __name__ == "__main__":
    asyncio.run(main())