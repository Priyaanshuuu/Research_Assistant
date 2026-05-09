import operator
from typing import Annotated, Any, TypedDict


class SearchResult(TypedDict):
    """Raw result returned by the Searcher node."""
    query: str
    url: str
    title: str
    content: str
    published_date: str | None


class EvaluatedResult(TypedDict):
    """Search result enriched with scores by the Evaluator node."""
    query: str
    url: str
    title: str
    content: str
    published_date: str | None
    credibility_score: float   # 0.0–1.0
    relevance_score: float     # 0.0–1.0
    combined_score: float      # weighted average


class ReportSection(TypedDict):
    heading: str
    body: str
    citations: list[str]       # list of URLs


class ResearchReport(TypedDict):
    title: str
    summary: str
    sections: list[ReportSection]
    all_citations: list[str]
    topic: str
    generated_at: str


class ResearchState(TypedDict):
    """
    Single source of truth flowing through the LangGraph state machine.

    Reducer notes:
    - raw_results / evaluated_results use operator.add — each Searcher pass
      appends new results rather than overwriting, so the Synthesizer sees
      everything gathered across all iterations.
    - All other fields are last-write-wins (standard LangGraph default).
    """

    # ── Identity (set by caller, never mutated) ───────────────────────────
    session_id: str
    user_id: str
    topic: str

    # ── Planner outputs ───────────────────────────────────────────────────
    sub_questions: list[str]
    search_queries: list[str]

    # ── Searcher outputs (accumulated across iterations) ──────────────────
    raw_results: Annotated[list[SearchResult], operator.add]

    # ── Evaluator outputs (accumulated across iterations) ─────────────────
    evaluated_results: Annotated[list[EvaluatedResult], operator.add]

    # ── Evaluator control ─────────────────────────────────────────────────
    needs_more_search: bool
    search_iterations: int     # incremented by evaluator each pass

    # ── Synthesizer output ────────────────────────────────────────────────
    synthesis: str

    # ── Writer output ─────────────────────────────────────────────────────
    report: ResearchReport

    # ── Meta ──────────────────────────────────────────────────────────────
    status: str                # pending | searching | evaluating | synthesizing | writing | completed
    error: str | None