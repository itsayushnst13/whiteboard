import secrets

from app.dependencies.db import DbSession
from app.exceptions import NotFoundError
from app.models.board import Board
from app.repositories.board_repository import BoardRepository
from app.schemas.board import BoardCreateRequest, BoardResponse, BoardUpdateRequest


class BoardService:
    """Board CRUD, scoped to a single owner — every read/write takes the
    requesting user's id and refuses to touch boards it doesn't own."""

    def __init__(self, session: DbSession) -> None:
        self._session = session
        self._boards = BoardRepository(session)

    async def list_boards(self, owner_id: int) -> list[BoardResponse]:
        boards = await self._boards.list_for_owner(owner_id)
        return [_to_response(board) for board in boards]

    async def create_board(self, owner_id: int, payload: BoardCreateRequest) -> BoardResponse:
        board = await self._boards.create(
            Board(room_id=secrets.token_urlsafe(9), name=payload.name, owner_id=owner_id)
        )
        await self._session.commit()
        return _to_response(board)

    async def get_board(self, owner_id: int, board_id: int) -> BoardResponse:
        board = await self._get_owned(owner_id, board_id)
        return _to_response(board)

    async def rename_board(
        self, owner_id: int, board_id: int, payload: BoardUpdateRequest
    ) -> BoardResponse:
        board = await self._get_owned(owner_id, board_id)
        board.name = payload.name
        await self._session.commit()
        await self._session.refresh(board)
        return _to_response(board)

    async def delete_board(self, owner_id: int, board_id: int) -> None:
        board = await self._get_owned(owner_id, board_id)
        await self._boards.delete(board)
        await self._session.commit()

    async def _get_owned(self, owner_id: int, board_id: int) -> Board:
        board = await self._boards.get_by_id(board_id)
        if board is None or board.owner_id != owner_id:
            raise NotFoundError("Board not found")
        return board


def _to_response(board: Board) -> BoardResponse:
    return BoardResponse(
        id=board.id,
        room_id=board.room_id,
        name=board.name,
        created_at=board.created_at,
        updated_at=board.updated_at,
    )
