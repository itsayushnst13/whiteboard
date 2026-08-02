from collections.abc import Sequence

from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board_collaborator import BoardCollaborator
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class BoardCollaboratorRepository(BaseRepository[BoardCollaborator]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, BoardCollaborator)

    async def get(self, board_id: int, user_id: int) -> BoardCollaborator | None:
        result = await self._session.execute(
            select(BoardCollaborator).where(
                BoardCollaborator.board_id == board_id,
                BoardCollaborator.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_board(self, board_id: int) -> Sequence[Row[tuple[BoardCollaborator, User]]]:
        result = await self._session.execute(
            select(BoardCollaborator, User)
            .join(User, User.id == BoardCollaborator.user_id)
            .where(BoardCollaborator.board_id == board_id)
            .order_by(BoardCollaborator.created_at.asc())
        )
        return result.all()
