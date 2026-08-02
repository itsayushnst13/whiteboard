import secrets

from app.dependencies.db import DbSession
from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.board import Board
from app.models.board_collaborator import BoardCollaborator
from app.repositories.board_collaborator_repository import BoardCollaboratorRepository
from app.repositories.board_repository import BoardRepository
from app.repositories.user_repository import UserRepository
from app.schemas.board import (
    BoardCreateRequest,
    BoardResponse,
    BoardRole,
    BoardUpdateRequest,
    CollaboratorResponse,
    ShareBoardRequest,
)


class BoardService:
    """Board CRUD plus sharing. Every board is owned by exactly one user
    (`Board.owner_id`) and may additionally have any number of
    collaborators (`BoardCollaborator` rows) with role `editor` or
    `viewer`. All access checks funnel through `_get_board_and_role` so
    "not found" (404) and "found but not allowed" (403) stay consistent
    and are never confused with each other."""

    def __init__(self, session: DbSession) -> None:
        self._session = session
        self._boards = BoardRepository(session)
        self._collaborators = BoardCollaboratorRepository(session)
        self._users = UserRepository(session)

    async def list_boards(self, user_id: int) -> list[BoardResponse]:
        rows = await self._boards.list_accessible_for_user(user_id)
        return [_to_response(board, role) for board, role in rows]

    async def create_board(self, owner_id: int, payload: BoardCreateRequest) -> BoardResponse:
        board = await self._boards.create(
            Board(room_id=secrets.token_urlsafe(9), name=payload.name, owner_id=owner_id)
        )
        await self._session.commit()
        return _to_response(board, "owner")

    async def get_board(self, user_id: int, board_id: int) -> BoardResponse:
        board, role = await self._get_board_and_role(board_id, user_id)
        return _to_response(board, role)

    async def rename_board(
        self, user_id: int, board_id: int, payload: BoardUpdateRequest
    ) -> BoardResponse:
        board = await self._require_owner(board_id, user_id)
        board.name = payload.name
        await self._session.commit()
        await self._session.refresh(board)
        return _to_response(board, "owner")

    async def delete_board(self, user_id: int, board_id: int) -> None:
        board = await self._require_owner(board_id, user_id)
        await self._boards.delete(board)
        await self._session.commit()

    async def share_board(
        self, owner_id: int, board_id: int, payload: ShareBoardRequest
    ) -> CollaboratorResponse:
        """Invite (or update the role of) a collaborator by email. Owner
        only. Adding the owner's own email, or an email with no matching
        account, is rejected with a clear message rather than a bare 404
        so the share dialog can show it inline."""
        await self._require_owner(board_id, owner_id)

        target = await self._users.get_by_email(payload.email)
        if target is None:
            raise NotFoundError("No account found with that email — ask them to sign up first")
        if target.id == owner_id:
            raise ConflictError("You already own this board")

        existing = await self._collaborators.get(board_id, target.id)
        if existing is not None:
            existing.role = payload.role
            await self._session.commit()
            await self._session.refresh(existing)
            collaborator = existing
        else:
            collaborator = await self._collaborators.create(
                BoardCollaborator(board_id=board_id, user_id=target.id, role=payload.role)
            )
            await self._session.commit()

        return CollaboratorResponse(
            user_id=target.id,
            email=target.email,
            display_name=target.display_name,
            role=collaborator.role,
            created_at=collaborator.created_at,
        )

    async def remove_collaborator(self, owner_id: int, board_id: int, target_user_id: int) -> None:
        await self._require_owner(board_id, owner_id)
        collaborator = await self._collaborators.get(board_id, target_user_id)
        if collaborator is None:
            raise NotFoundError("That person isn't a collaborator on this board")
        await self._collaborators.delete(collaborator)
        await self._session.commit()

    async def list_collaborators(self, user_id: int, board_id: int) -> list[CollaboratorResponse]:
        await self._get_board_and_role(board_id, user_id)
        rows = await self._collaborators.list_for_board(board_id)
        return [
            CollaboratorResponse(
                user_id=user.id,
                email=user.email,
                display_name=user.display_name,
                role=collaborator.role,
                created_at=collaborator.created_at,
            )
            for collaborator, user in rows
        ]

    async def _get_board_and_role(self, board_id: int, user_id: int) -> tuple[Board, BoardRole]:
        board = await self._boards.get_by_id(board_id)
        if board is None:
            raise NotFoundError("Board not found")
        if board.owner_id == user_id:
            return board, "owner"
        collaborator = await self._collaborators.get(board_id, user_id)
        if collaborator is None:
            raise ForbiddenError("You don't have access to this board")
        return board, collaborator.role  # type: ignore[return-value]

    async def _require_owner(self, board_id: int, user_id: int) -> Board:
        board, role = await self._get_board_and_role(board_id, user_id)
        if role != "owner":
            raise ForbiddenError("Only the board owner can do this")
        return board


def _to_response(board: Board, role: BoardRole) -> BoardResponse:
    return BoardResponse(
        id=board.id,
        room_id=board.room_id,
        name=board.name,
        owner_id=board.owner_id,
        role=role,
        created_at=board.created_at,
        updated_at=board.updated_at,
    )
