import hashlib
import json

import redis.asyncio as aioredis
from loguru import logger

from core.config import settings

SEARCH_CACHE_TTL = 60 * 60 * 24   # 24 hours

_pool: aioredis.ConnectionPool | None = None


def _get_pool() -> aioredis.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = aioredis.ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=20,
        )
    return _pool


def _client() -> aioredis.Redis:
    return aioredis.Redis(connection_pool=_get_pool())


def _cache_key(query: str) -> str:
    digest = hashlib.sha256(query.lower().strip().encode()).hexdigest()[:16]
    return f"search:v1:{digest}"


async def get_cached_results(query: str) -> list[dict] | None:
    """Returns cached Tavily results or None on cache miss."""
    try:
        raw = await _client().get(_cache_key(query))
        if raw:
            logger.debug("[redis] Cache HIT — '{}'", query[:60])
            return json.loads(raw)
        logger.debug("[redis] Cache MISS — '{}'", query[:60])
        return None
    except Exception as exc:
        logger.warning("[redis] get_cached_results error: {}", exc)
        return None


async def set_cached_results(query: str, results: list[dict]) -> None:
    """Stores search results in Redis with a 24-hour TTL."""
    try:
        await _client().setex(
            _cache_key(query),
            SEARCH_CACHE_TTL,
            json.dumps(results),
        )
        logger.debug("[redis] Cached {} results — '{}'", len(results), query[:60])
    except Exception as exc:
        logger.warning("[redis] set_cached_results error: {}", exc)


async def increment_rate_limit(key: str, window_seconds: int = 60) -> int:
    """
    Increments a sliding-window counter for rate limiting.
    Returns the new count. Sets TTL on first increment.
    Used in Day 6 FastAPI middleware.
    """
    try:
        rkey = f"rl:{key}"
        pipe = _client().pipeline()
        await pipe.incr(rkey)
        await pipe.expire(rkey, window_seconds)
        results = await pipe.execute()
        return int(results[0])
    except Exception as exc:
        logger.warning("[redis] increment_rate_limit error: {}", exc)
        return 0


async def get_rate_limit_count(key: str) -> int:
    """Returns current rate-limit counter without incrementing."""
    try:
        val = await _client().get(f"rl:{key}")
        return int(val) if val else 0
    except Exception as exc:
        logger.warning("[redis] get_rate_limit_count error: {}", exc)
        return 0