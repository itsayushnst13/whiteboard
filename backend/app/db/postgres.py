import logging
from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_engine() -> AsyncEngine:
    """Lazily-created, process-wide async engine. Creating an engine does
    not open a connection — the pool connects on first use — so the app
    can start even if Postgres isn't reachable yet."""
    settings = get_settings()
    return create_async_engine(
        settings.DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,
        echo=settings.DEBUG,
    )


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=get_engine(), expire_on_commit=False, autoflush=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Request-scoped session generator, wired into the app via the
    `get_db` FastAPI dependency."""
    async with get_sessionmaker()() as session:
        yield session


async def ping_database() -> bool:
    """Used by the readiness probe to confirm Postgres is reachable."""
    try:
        async with get_engine().connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.exception("Database readiness check failed")
        return False
