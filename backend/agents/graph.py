# REPLACE THIS FILE — adds key_takeaways to printed output

import asyncio
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from agents.graph import get_research_graph
from agents.state import ResearchState


async def run(topic: str) -> None:
    session_id = str(uuid.uuid4())
    thread_id = f"test-{session_id[:8]}"

    logger.info(
        "Starting research graph — topic: '{}' | thread: {}", topic, thread_id
    )

    initial_state: ResearchState = {
        "session_id": session_id,
        "user_id": "test-user-001",
        "topic": topic,
        "sub_questions": [],
        "search_queries": [],
        "raw_results": [],
        "evaluated_results": [],
        "needs_more_search": False,
        "search_iterations": 0,
        "synthesis": "",
        "report": {},           # type: ignore[typeddict-item]
        "status": "pending",
        "error": None,
    }

    run_config = {"configurable": {"thread_id": thread_id}}

    async with get_research_graph() as graph:
        try:
            final = await graph.ainvoke(initial_state, config=run_config)

            report = final.get("report", {})

            print("\n" + "=" * 70)
            print("RESEARCH COMPLETE")
            print("=" * 70)
            print(f"Status    : {final['status']}")
            print(f"Topic     : {final['topic']}")
            print(f"Title     : {report.get('title', 'N/A')}")
            print(f"Sections  : {len(report.get('sections', []))}")
            print(f"Citations : {len(report.get('all_citations', []))}")
            print(f"Iterations: {final['search_iterations']}")

            print("\n── Executive Summary " + "─" * 49)
            print(report.get("summary", "N/A"))

            takeaways = report.get("key_takeaways", [])
            if takeaways:
                print("\n── Key Takeaways " + "─" * 53)
                for i, t in enumerate(takeaways, 1):
                    print(f"  {i}. {t}")

            print("\n── Section Headings " + "─" * 50)
            for i, s in enumerate(report.get("sections", []), 1):
                print(f"  {i}. {s['heading']}")

            print("\n── Citations " + "─" * 57)
            for url in report.get("all_citations", [])[:8]:
                print(f"  • {url}")

            if final.get("error"):
                print(f"\n⚠  Error in state: {final['error']}")

            print("\n── Full Report JSON saved to: report_output.json")
            with open("report_output.json", "w") as f:
                json.dump(report, f, indent=2)

        except Exception as exc:
            logger.error("Graph execution failed: {}", exc)
            raise


if __name__ == "__main__":
    topic = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "Impact of large language models on software engineering"
    )
    asyncio.run(run(topic))