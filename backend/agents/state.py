from typing import TypedDict, Optional
from datetime import datetime


class SearchResult(TypedDict):
    """A single search result from Tavily."""
    query: str
    url: str
    title: str
    content: str
    published_date: Optional[str]


class EvaluatedResult(TypedDict):
    """A search result that has been evaluated for relevance."""
    query: str
    url: str
    title: str
    content: str
    published_date: Optional[str]
    relevance_score: float
    reasoning: str


class ReportSection(TypedDict):
    """A section of the research report."""
    heading: str
    body: str
    citations: list[str]


class ResearchReport(TypedDict):
    """The final research report."""
    title: str
    summary: str
    key_takeaways: list[str]
    sections: list[ReportSection]
    all_citations: list[str]
    generated_at: str


class ResearchState(TypedDict):
    """The research workflow state."""
    session_id: str
    user_id: str
    topic: str
    sub_questions: list[str]
    search_queries: list[str]
    raw_results: list[SearchResult]
    evaluated_results: list[EvaluatedResult]
    needs_more_search: bool
    search_iterations: int
    synthesis: str
    report: ResearchReport
    status: str
    error: Optional[str]