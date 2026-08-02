from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.repositories.base_repository import BaseRepository


class BoardRepository(BaseRepository[Board]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Board)

    async def list_for_owner(self, owner_id: int) -> Sequence[Board]:
        result = await self._session.execute(
            select(Board).where(Board.owner_id == owner_id).order_by(Board.updated_at.desc())
        )
        return result.scalars().all()

    async def get_by_room_id(self, room_id: str) -> Board | None:
        result = await self._session.execute(select(Board).where(Board.room_id == room_id))
        return result.scalar_one_or_none()
