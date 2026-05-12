from typing import TypedDict, Optional


class SearchResult(TypedDict):
    """A single search result from Tavily."""
    query: str
    url: str
    title: str
    content: str
    published_date: Optional[str]


class ResearchState(TypedDict):
    """The research workflow state."""
    session_id: str
    user_id: str
    topic: str
    sub_questions: list[str]
    search_queries: list[str]
    raw_results: list[SearchResult]
    evaluated_results: list[SearchResult]
    needs_more_search: bool
    search_iterations: int
    synthesis: str
    report: dict
    status: str
    error: Optional[str]