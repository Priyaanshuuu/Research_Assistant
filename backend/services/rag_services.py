import uuid

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from loguru import logger
from sqlalchemy.orm import Session

from core.config import settings
from db.models import ChatMessage, MessageRole
from services.pinecone_service import query_similar
TOP_K_CHUNKS = 6

MAX_HISTORY_TURNS = 6

_RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a knowledgeable research assistant helping a user explore \
a completed research report.

You have access to the relevant excerpts from the research sources below. \
Use them to answer the user's question accurately and concisely.

Rules:
- Base your answer primarily on the provided source excerpts
- If the excerpts don't contain enough information, say so clearly — \
  do not fabricate facts
- Cite sources inline as [Source Title] when referencing specific claims
- Keep answers focused and well-structured — use short paragraphs
- If the user asks something unrelated to the research topic, \
  gently redirect them

Research topic: {topic}

Relevant source excerpts:
{context}""",
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

def _save_message(
    db: Session,
    session_id: str,
    role: MessageRole,
    content: str,
) -> ChatMessage:
    msg = ChatMessage(
        id=uuid.uuid4(),
        session_id=uuid.UUID(session_id),
        role=role,
        content=content,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def _load_history(db: Session, session_id: str) -> list[BaseMessage]:
    """
    Loads the last MAX_HISTORY_TURNS pairs of messages from Postgres
    and converts them to LangChain message objects.
    """
    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == uuid.UUID(session_id))
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    max_msgs = MAX_HISTORY_TURNS * 2
    rows = rows[-max_msgs:] if len(rows) > max_msgs else rows

    history: list[BaseMessage] = []
    for row in rows:
        if row.role == MessageRole.USER:
            history.append(HumanMessage(content=row.content))
        elif row.role == MessageRole.ASSISTANT:
            history.append(AIMessage(content=row.content))

    return history


def _format_context(chunks: list[dict]) -> str:
    """Formats Pinecone matches into a numbered context block for the prompt."""
    if not chunks:
        return "No relevant source excerpts found."

    parts: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        title = chunk.get("title", "Unknown source")
        url = chunk.get("url", "")
        content = chunk.get("content", "")
        score = chunk.get("score", 0.0)
        parts.append(
            f"[{i}] {title}\n"
            f"    URL: {url}\n"
            f"    Relevance: {score:.2f}\n"
            f"    Excerpt: {content}"
        )

    return "\n\n".join(parts)

async def answer_question(
    db: Session,
    session_id: str,
    topic: str,
    question: str,
) -> tuple[ChatMessage, ChatMessage]:
    """
    Full RAG pipeline:
      1. Retrieve relevant chunks from Pinecone (scoped to session namespace)
      2. Load conversation history from Postgres
      3. Build prompt with context + history + question
      4. Call GPT-4o for a grounded answer
      5. Persist both user message and assistant response to Postgres
      6. Return (user_message, assistant_message) DB rows

    Raises on LLM or DB failure — caller handles HTTP errors.
    """
    logger.info(
        "[rag] Answering question for session {} — '{}...'",
        session_id[:8],
        question[:60],
    )

    try:
    
        chunks = await query_similar(
            session_id=session_id,
            query=question,
            top_k=TOP_K_CHUNKS,
        )
        logger.info("[rag] Retrieved {} chunks from Pinecone", len(chunks))

        # ── 2. Conversation history ───────────────────────────────────────
        history = _load_history(db, session_id)
        logger.debug("[rag] Loaded {} history messages", len(history))

        # ── 3. Persist user message ───────────────────────────────────────
        user_msg = _save_message(db, session_id, MessageRole.USER, question)

        # ── 4. LLM call ───────────────────────────────────────────────────
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY,
        )

        chain = _RAG_PROMPT | llm

        response = await chain.ainvoke(
            {
                "topic": topic,
                "context": _format_context(chunks),
                "history": history,
                "question": question,
            }
        )

        answer: str = response.content.strip()
        logger.info("[rag] Answer generated — {} chars", len(answer))

        # ── 5. Persist assistant message ──────────────────────────────────
        assistant_msg = _save_message(
            db, session_id, MessageRole.ASSISTANT, answer
        )

        return user_msg, assistant_msg

    except Exception as exc:
        logger.error("[rag] answer_question failed: {}", exc)
        raise


async def get_chat_history(
    db: Session,
    session_id: str,
) -> list[ChatMessage]:
    """Returns all chat messages for a session ordered oldest → newest."""
    try:
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == uuid.UUID(session_id))
            .order_by(ChatMessage.created_at.asc())
            .all()
        )
    except Exception as exc:
        logger.error("[rag] get_chat_history failed: {}", exc)
        return []