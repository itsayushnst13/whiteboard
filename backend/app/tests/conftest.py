import os

# Settings validation requires these; tests never talk to real infra, but
# Settings() must still construct successfully at import time. Set before
# any `app.*` import so the first get_settings() call picks these up.
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")

from collections.abc import AsyncIterator  # noqa: E402

import pytest  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.core.app_factory import create_app  # noqa: E402
from app.db.postgres import get_db_session  # noqa: E402
from app.models import Base  # noqa: E402


@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_app(app: FastAPI) -> AsyncIterator[FastAPI]:
    """An app instance wired to a throwaway in-memory SQLite database, for
    tests that exercise real persistence (auth, boards) rather than just
    mocked health checks. A single shared connection is used so the
    in-memory database survives across the multiple connections a session
    pool would otherwise open."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

    async def override_get_db_session() -> AsyncIterator[AsyncSession]:
        async with sessionmaker() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session
    try:
        yield app
    finally:
        app.dependency_overrides.pop(get_db_session, None)
        await engine.dispose()


@pytest.fixture
async def db_client(db_app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=db_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
