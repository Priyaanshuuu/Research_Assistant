from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import BaseModel, Field

from agents.state import ResearchState
from core.config import settings


class PlannerOutput(BaseModel):
    """Structured output schema enforced by GPT-4o."""

    sub_questions: list[str] = Field(
        description=(
            "5-7 specific, non-overlapping sub-questions that together give "
            "comprehensive coverage of the research topic"
        ),
        min_length=3,
        max_length=8,
    )
    search_queries: list[str] = Field(
        description=(
            "One precise web search query per sub-question, "
            "optimised for finding authoritative and recent sources"
        ),
        min_length=3,
        max_length=8,
    )
    reasoning: str = Field(
        description="One-sentence explanation of the decomposition strategy chosen"
    )


_PLANNER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert research strategist. Given a research topic:

1. Break it into 5-7 specific, non-overlapping sub-questions that together \
give complete coverage (definition, current state, challenges, applications, future).
2. Write one precise search query per sub-question — include "2024" where recency matters, \
prefer specific terms over broad ones.

Rules:
- Each sub-question must be independently answerable
- Queries must be distinct — no overlapping intent
- Avoid filler words in queries; be direct and keyword-rich""",
        ),
        ("human", "Research topic: {topic}"),
    ]
)


async def planner_node(state: ResearchState) -> dict:
    """
    Input:  state["topic"]
    Output: sub_questions, search_queries, status
    """
    topic = state["topic"]
    logger.info("[planner] Starting — topic: '{}'", topic)

    try:
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.2,
            openai_api_key=settings.OPENAI_API_KEY,
        )

        chain = _PLANNER_PROMPT | llm.with_structured_output(PlannerOutput)

        result: PlannerOutput = await chain.ainvoke({"topic": topic})

        logger.info(
            "[planner] {} sub-questions | {} queries | strategy: {}",
            len(result.sub_questions),
            len(result.search_queries),
            result.reasoning[:120],
        )

        return {
            "sub_questions": result.sub_questions,
            "search_queries": result.search_queries,
            "status": "searching",
        }

    except Exception as exc:
        logger.error("[planner] Failed: {}", exc)
        return {"error": str(exc), "status": "failed"}