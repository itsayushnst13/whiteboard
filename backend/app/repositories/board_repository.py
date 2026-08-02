from collections.abc import Sequence

from sqlalchemy import Row, and_, case, literal, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.models.board_collaborator import BoardCollaborator
from app.repositories.base_repository import BaseRepository


class BoardRepository(BaseRepository[Board]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Board)

    async def list_for_owner(self, owner_id: int) -> Sequence[Board]:
        result = await self._session.execute(
            select(Board).where(Board.owner_id == owner_id).order_by(Board.updated_at.desc())
        )
        return result.scalars().all()

    async def list_accessible_for_user(self, user_id: int) -> Sequence[Row[tuple[Board, str]]]:
        """Every board the user can open — owned or shared with them —
        paired with their role on it. One row per board even if somehow
        matched by both conditions, since the join is scoped to this
        user's own collaborator row."""
        role_expr = case(
            (Board.owner_id == user_id, literal("owner")),
            else_=BoardCollaborator.role,
        ).label("role")

        result = await self._session.execute(
            select(Board, role_expr)
            .outerjoin(
                BoardCollaborator,
                and_(
                    BoardCollaborator.board_id == Board.id,
                    BoardCollaborator.user_id == user_id,
                ),
            )
            .where(or_(Board.owner_id == user_id, BoardCollaborator.user_id == user_id))
            .order_by(Board.updated_at.desc())
        )
        return result.all()

    async def get_by_room_id(self, room_id: str) -> Board | None:
        result = await self._session.execute(select(Board).where(Board.room_id == room_id))
        return result.scalar_one_or_none()
