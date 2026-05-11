import uuid
from typing import Any

from langchain_openai import OpenAIEmbeddings
from loguru import logger
from pinecone import Pinecone, ServerlessSpec

from core.config import settings

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536
CHUNK_SIZE = 500     
CHUNK_OVERLAP = 100   

_pc: Pinecone | None = None
_embeddings: OpenAIEmbeddings | None = None


def _get_pinecone() -> Pinecone:
    global _pc
    if _pc is None:
        _pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    return _pc


def _get_embeddings() -> OpenAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
        )
    return _embeddings


def _get_index() -> Any:
    """Returns the Pinecone index, creating it first if it doesn't exist."""
    pc = _get_pinecone()
    existing = pc.list_indexes().names()

    if settings.PINECONE_INDEX_NAME not in existing:
        logger.info("[pinecone] Creating index '{}'", settings.PINECONE_INDEX_NAME)
        pc.create_index(
            name=settings.PINECONE_INDEX_NAME,
            dimension=EMBEDDING_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        logger.info("[pinecone] Index created successfully")

    return pc.Index(settings.PINECONE_INDEX_NAME)


def _chunk_text(text: str) -> list[str]:
    """Splits text into overlapping fixed-size chunks."""
    if len(text) <= CHUNK_SIZE:
        return [text] if text.strip() else []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks

async def upsert_search_results(
    session_id: str,
    results: list[dict],
) -> int:
    """
    Embeds and upserts search result content into Pinecone.
    Namespaced by session_id — RAG queries in Day 8 stay scoped to one session.
    Returns total number of vectors upserted.
    """
    if not results:
        return 0

    try:
        index = _get_index()
        embedder = _get_embeddings()

        vectors: list[dict] = []

        for result in results:
            content = (result.get("content") or "").strip()
            if not content:
                continue

            chunks = _chunk_text(content)
            if not chunks:
                continue

            embeddings = await embedder.aembed_documents(chunks)

            for chunk_idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = f"{session_id[:8]}-{uuid.uuid4().hex[:8]}-{chunk_idx}"
                vectors.append(
                    {
                        "id": vector_id,
                        "values": embedding,
                        "metadata": {
                            "session_id": session_id,
                            "url": result.get("url", ""),
                            "title": result.get("title", ""),
                            "content": chunk,
                            "query": result.get("query", ""),
                            "published_date": result.get("published_date") or "",
                        },
                    }
                )

        if not vectors:
            logger.warning("[pinecone] No embeddable content in results")
            return 0

        batch_size = 100
        total = 0
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i : i + batch_size]
            index.upsert(vectors=batch, namespace=session_id)
            total += len(batch)

        logger.info(
            "[pinecone] Upserted {} vectors for session {}",
            total,
            session_id[:8],
        )
        return total

    except Exception as exc:
        logger.error("[pinecone] upsert_search_results failed: {}", exc)
        return 0


async def query_similar(
    session_id: str,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Retrieves top_k most similar content chunks for a query within a session.
    Called by the RAG chain in Day 8.
    """
    try:
        index = _get_index()
        embedder = _get_embeddings()

        query_embedding = await embedder.aembed_query(query)

        response = index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace=session_id,
            include_metadata=True,
        )

        results = []
        for match in response.get("matches", []):
            meta = match.get("metadata", {})
            results.append(
                {
                    "score": round(match["score"], 4),
                    "content": meta.get("content", ""),
                    "url": meta.get("url", ""),
                    "title": meta.get("title", ""),
                    "query": meta.get("query", ""),
                }
            )

        logger.info(
            "[pinecone] Query returned {} matches for session {}",
            len(results),
            session_id[:8],
        )
        return results

    except Exception as exc:
        logger.error("[pinecone] query_similar failed: {}", exc)
        return []