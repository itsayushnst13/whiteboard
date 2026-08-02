import logging
from functools import lru_cache

from redis.asyncio import Redis
from redis.asyncio import from_url as redis_from_url

from app.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_redis_client() -> Redis:
    """Lazily-created, process-wide Redis client. `from_url` builds a
    connection pool without connecting immediately, mirroring the async
    Postgres engine's lazy-connect behavior."""
    settings = get_settings()
    # redis-py's `from_url` isn't typed precisely enough for mypy --strict
    # to infer past `Any` here.
    client: Redis = redis_from_url(  # type: ignore[no-untyped-call]
        settings.REDIS_URL, decode_responses=True
    )
    return client


async def ping_redis() -> bool:
    """Used by the readiness probe to confirm Redis is reachable."""
    try:
        return bool(await get_redis_client().ping())
    except Exception:
        logger.exception("Redis readiness check failed")
        return False
