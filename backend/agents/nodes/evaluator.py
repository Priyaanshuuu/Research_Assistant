import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import BaseModel, Field
from tiktoken import encoding_for_model

from agents.state import EvaluatedResult, ResearchState
from core.config import settings

MAX_ITERATIONS = 3
QUALITY_THRESHOLD = 0.60

TOKEN_BUDGET = 80_000

_ENCODER = encoding_for_model("gpt-4o")

def _count_tokens(texts: list[str]) -> int:
    return sum(len(_ENCODER.encode(t)) for t in texts if t)


def _budget_exceeded(state: ResearchState) -> bool:
    all_content = [r["content"] for r in state["raw_results"]]
    total = _count_tokens(all_content)
    if total >= TOKEN_BUDGET:
        logger.warning(
            "[evaluator] Token budget exceeded — {} tokens (limit {})",
            total,
            TOKEN_BUDGET,
        )
    return total >= TOKEN_BUDGET
class ResultScore(BaseModel):
    credibility_score: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "How credible is the source? Consider: known domain authority, "
            "presence of author/date, academic or official source (1.0), "
            "anonymous blog with no date (0.2)"
        ),
    )
    relevance_score: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "How relevant is the content to the research query? "
            "Directly answers the query (1.0), tangentially related (0.3), "
            "off-topic (0.0)"
        ),
    )
    reasoning: str = Field(
        description="One sentence justifying both scores"
    )


class BatchScores(BaseModel):
    scores: list[ResultScore] = Field(
        description="One score object per result, in the same order as the input list"
    )


_EVALUATOR_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a research quality evaluator. You will receive a research topic \
and a list of search results. For each result, assign:

- credibility_score (0.0–1.0): authority and trustworthiness of the source
- relevance_score   (0.0–1.0): how directly the content answers the query

Scoring guide:
  credibility: .gov/.edu/peer-reviewed = 0.9-1.0 | major news/industry = 0.7-0.8 | \
blog/unknown = 0.3-0.5 | no source info = 0.1-0.2
  relevance: directly answers query = 0.8-1.0 | partial = 0.4-0.7 | tangential = 0.0-0.3

Return exactly one score object per result in input order.""",
        ),
        (
            "human",
            """Research topic: {topic}

Results to score:
{results_json}""",
        ),
    ]
)

async def evaluator_node(state: ResearchState) -> dict:
    """
    Input:  state["raw_results"], state["search_iterations"], state["topic"]
    Output: evaluated_results (appended via reducer), needs_more_search,
            search_iterations (incremented), status
    """
    iteration = state["search_iterations"]
    all_raw = state["raw_results"]
    results_per_iter = len(state["search_queries"])
    latest_raw = all_raw[iteration * results_per_iter :] 

    logger.info(
        "[evaluator] Scoring {} results (iteration {})",
        len(latest_raw),
        iteration + 1,
    )

    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
            openai_api_key=settings.OPENAI_API_KEY,
        )

        chain = _EVALUATOR_PROMPT | llm.with_structured_output(BatchScores)

        results_for_prompt = [
            {
                "index": i,
                "query": r["query"],
                "url": r["url"],
                "title": r["title"],
                "content": r["content"][:600], 
            }
            for i, r in enumerate(latest_raw)
        ]

        batch: BatchScores = await chain.ainvoke(
            {
                "topic": state["topic"],
                "results_json": json.dumps(results_for_prompt, indent=2),
            }
        )
        while len(batch.scores) < len(latest_raw):
            batch.scores.append(
                ResultScore(
                    credibility_score=0.5,
                    relevance_score=0.5,
                    reasoning="Score unavailable — default applied",
                )
            )

        evaluated: list[EvaluatedResult] = []
        for raw, score in zip(latest_raw, batch.scores):
            combined = round(
                score.credibility_score * 0.4 + score.relevance_score * 0.6, 4
            )
            evaluated.append(
                EvaluatedResult(
                    query=raw["query"],
                    url=raw["url"],
                    title=raw["title"],
                    content=raw["content"],
                    published_date=raw.get("published_date"),
                    credibility_score=round(score.credibility_score, 4),
                    relevance_score=round(score.relevance_score, 4),
                    combined_score=combined,
                )
            )

        avg_score = sum(r["combined_score"] for r in evaluated) / max(len(evaluated), 1)
        new_iteration = iteration + 1
        budget_hit = _budget_exceeded(state)
        needs_more = (
            avg_score < QUALITY_THRESHOLD
            and new_iteration < MAX_ITERATIONS
            and not budget_hit
        )

        logger.info(
            "[evaluator] Avg score: {:.3f} | needs_more: {} | budget_exceeded: {} | iteration: {}",
            avg_score,
            needs_more,
            budget_hit,
            new_iteration,
        )

        for r in evaluated[:3]:
            logger.debug(
                "[evaluator] {} | cred={} rel={} combined={}",
                r["title"][:60],
                r["credibility_score"],
                r["relevance_score"],
                r["combined_score"],
            )

        return {
            "evaluated_results": evaluated,
            "needs_more_search": needs_more,
            "search_iterations": new_iteration,
            "status": "searching" if needs_more else "synthesizing",
        }

    except Exception as exc:
        logger.error("[evaluator] Failed: {}", exc)
        return {"error": str(exc), "status": "failed"}


def routing_decision(state: ResearchState) -> str:
    """
    Conditional edge — called by LangGraph after evaluator_node.
    Unchanged from Day 3; routing logic is now driven by real scores.
    """
    if state.get("needs_more_search") and state["search_iterations"] < MAX_ITERATIONS:
        logger.info(
            "[router] Routing back to searcher — iteration {}",
            state["search_iterations"] + 1,
        )
        return "searcher"

    logger.info("[router] Routing to synthesizer")
    return "synthesizer"