from fastapi import APIRouter, Request, status

from app.dependencies import BoardServiceDep, CurrentUser
from app.schemas import (
    ApiResponse,
    BoardCreateRequest,
    BoardResponse,
    BoardUpdateRequest,
    CollaboratorResponse,
    ShareBoardRequest,
)
from app.utils.request_context import get_request_id

router = APIRouter(prefix="/boards", tags=["boards"])


@router.get("", response_model=ApiResponse[list[BoardResponse]])
async def list_boards(
    request: Request, current_user: CurrentUser, service: BoardServiceDep
) -> ApiResponse[list[BoardResponse]]:
    """Every board the user owns or has been invited to, newest first.
    Each entry carries the caller's `role` on it so the frontend can
    split "Owned boards" from "Shared with me" without a second call."""
    data = await service.list_boards(current_user.id)
    return ApiResponse.ok(data, request_id=get_request_id(request))


@router.post("", response_model=ApiResponse[BoardResponse], status_code=status.HTTP_201_CREATED)
async def create_board(
    request: Request,
    payload: BoardCreateRequest,
    current_user: CurrentUser,
    service: BoardServiceDep,
) -> ApiResponse[BoardResponse]:
    data = await service.create_board(current_user.id, payload)
    return ApiResponse.ok(data, request_id=get_request_id(request))


@router.get("/{board_id}", response_model=ApiResponse[BoardResponse])
async def get_board(
    request: Request, board_id: int, current_user: CurrentUser, service: BoardServiceDep
) -> ApiResponse[BoardResponse]:
    """404 if the board doesn't exist at all, 403 if it exists but the
    caller is neither the owner nor a collaborator."""
    data = await service.get_board(current_user.id, board_id)
    return ApiResponse.ok(data, request_id=get_request_id(request))


@router.patch("/{board_id}", response_model=ApiResponse[BoardResponse])
async def rename_board(
    request: Request,
    board_id: int,
    payload: BoardUpdateRequest,
    current_user: CurrentUser,
    service: BoardServiceDep,
) -> ApiResponse[BoardResponse]:
    data = await service.rename_board(current_user.id, board_id, payload)
    return ApiResponse.ok(data, request_id=get_request_id(request))


@router.delete("/{board_id}", response_model=ApiResponse[None])
async def delete_board(
    request: Request, board_id: int, current_user: CurrentUser, service: BoardServiceDep
) -> ApiResponse[None]:
    await service.delete_board(current_user.id, board_id)
    return ApiResponse.ok(None, request_id=get_request_id(request))


@router.post(
    "/{board_id}/share",
    response_model=ApiResponse[CollaboratorResponse],
    status_code=status.HTTP_201_CREATED,
)
async def share_board(
    request: Request,
    board_id: int,
    payload: ShareBoardRequest,
    current_user: CurrentUser,
    service: BoardServiceDep,
) -> ApiResponse[CollaboratorResponse]:
    """Primary action behind the Share dialog's "Invite" button — invite
    (or re-invite with a new role) a collaborator by email. Owner only."""
    data = await service.share_board(current_user.id, board_id, payload)
    return ApiResponse.ok(data, request_id=get_request_id(request))


@router.post(
    "/{board_id}/collaborators",
    response_model=ApiResponse[CollaboratorResponse],
    status_code=status.HTTP_201_CREATED,
)
async def add_collaborator(
    request: Request,
    board_id: int,
    payload: ShareBoardRequest,
    current_user: CurrentUser,
    service: BoardServiceDep,
) -> ApiResponse[CollaboratorResponse]:
    """REST-conventional equivalent of `POST /{board_id}/share` — same
    underlying operation, exposed as a resource-collection endpoint too
    (e.g. for changing an existing collaborator's role from the list)."""
    data = await service.share_board(current_user.id, board_id, payload)
    return ApiResponse.ok(data, request_id=get_request_id(request))


@router.get("/{board_id}/collaborators", response_model=ApiResponse[list[CollaboratorResponse]])
async def list_collaborators(
    request: Request, board_id: int, current_user: CurrentUser, service: BoardServiceDep
) -> ApiResponse[list[CollaboratorResponse]]:
    data = await service.list_collaborators(current_user.id, board_id)
    return ApiResponse.ok(data, request_id=get_request_id(request))


@router.delete("/{board_id}/collaborators/{user_id}", response_model=ApiResponse[None])
async def remove_collaborator(
    request: Request,
    board_id: int,
    user_id: int,
    current_user: CurrentUser,
    service: BoardServiceDep,
) -> ApiResponse[None]:
    await service.remove_collaborator(current_user.id, board_id, user_id)
    return ApiResponse.ok(None, request_id=get_request_id(request))
