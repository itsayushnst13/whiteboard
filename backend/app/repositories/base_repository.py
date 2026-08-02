from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic async CRUD operations shared by every table-backed
    repository. Domain repositories subclass this and add query methods
    specific to their model; no application tables exist yet, so nothing
    subclasses it in this milestone."""

    def __init__(self, session: AsyncSession, model: type[ModelType]) -> None:
        self._session = session
        self._model = model

    async def get_by_id(self, entity_id: int) -> ModelType | None:
        return await self._session.get(self._model, entity_id)

    async def list_all(self) -> Sequence[ModelType]:
        result = await self._session.execute(select(self._model))
        return result.scalars().all()

    async def create(self, instance: ModelType) -> ModelType:
        self._session.add(instance)
        await self._session.flush()
        return instance

    async def delete(self, instance: ModelType) -> None:
        await self._session.delete(instance)
        await self._session.flush()
