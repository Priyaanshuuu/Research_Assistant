"""
LangGraph research graph — compiles the state machine with async
PostgreSQL checkpointing. Exposes get_research_graph() as an async
context manager so callers own the connection lifecycle.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from loguru import logger

from agents.state import ResearchState
from agents.nodes.planner import planner_node
from agents.nodes.searcher import searcher_node
from agents.nodes.evaluator import evaluator_node, routing_decision
from agents.nodes.synthesizer import synthesizer_node
from agents.nodes.writer import writer_node
from core.config import settings


def _compile_graph(checkpointer: AsyncPostgresSaver):
    """
    Pure graph topology — no I/O.
    Called once per context-manager invocation.

    Flow:
      planner → searcher → evaluator ─┬─(needs_more_search)──→ searcher
                                       └─(quality met)─────────→ synthesizer → writer → END
    """
    builder = StateGraph(ResearchState)

    # ── Nodes ─────────────────────────────────────────────────────────────
    builder.add_node("planner", planner_node)
    builder.add_node("searcher", searcher_node)
    builder.add_node("evaluator", evaluator_node)
    builder.add_node("synthesizer", synthesizer_node)
    builder.add_node("writer", writer_node)

    # ── Edges ─────────────────────────────────────────────────────────────
    builder.set_entry_point("planner")
    builder.add_edge("planner", "searcher")
    builder.add_edge("searcher", "evaluator")
    builder.add_conditional_edges(
        "evaluator",
        routing_decision,
        {
            "searcher": "searcher",       # loop back for another search pass
            "synthesizer": "synthesizer", # quality threshold met
        },
    )
    builder.add_edge("synthesizer", "writer")
    builder.add_edge("writer", END)

    graph = builder.compile(checkpointer=checkpointer)
    logger.info("Research graph compiled successfully")
    return graph


@asynccontextmanager
async def get_research_graph() -> AsyncGenerator:
    """
    Async context manager — opens a Postgres connection for LangGraph
    checkpointing, yields a compiled graph, and closes the connection cleanly.

    Usage:
        async with get_research_graph() as graph:
            result = await graph.ainvoke(initial_state, config=config)
    """
    # psycopg3 uses plain postgresql:// (not postgresql+psycopg://)
    conn_string = settings.DATABASE_URL.replace("+psycopg2", "")

    try:
        async with AsyncPostgresSaver.from_conn_string(conn_string) as checkpointer:
            # Creates langgraph checkpoint tables if they don't already exist
            await checkpointer.setup()
            logger.debug("LangGraph Postgres checkpointer ready")
            yield _compile_graph(checkpointer)
    except Exception as exc:
        logger.error("Failed to initialise research graph: {}", exc)
        raise