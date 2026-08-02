from collections.abc import AsyncIterator

import pytest
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.repositories.base_repository import BaseRepository


class _Widget(Base):
    __tablename__ = "test_widgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        yield session

    await engine.dispose()


async def test_create_and_get_by_id(session: AsyncSession) -> None:
    repo = BaseRepository(session, _Widget)

    created = await repo.create(_Widget(name="alpha"))
    await session.commit()

    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "alpha"


async def test_list_all_returns_every_row(session: AsyncSession) -> None:
    repo = BaseRepository(session, _Widget)
    await repo.create(_Widget(name="one"))
    await repo.create(_Widget(name="two"))
    await session.commit()

    rows = await repo.list_all()
    assert {row.name for row in rows} == {"one", "two"}


async def test_delete_removes_row(session: AsyncSession) -> None:
    repo = BaseRepository(session, _Widget)
    widget = await repo.create(_Widget(name="temp"))
    await session.commit()

    await repo.delete(widget)
    await session.commit()

    assert await repo.get_by_id(widget.id) is None
