from fastapi import APIRouter, Request, status

from app.dependencies import BoardServiceDep, CurrentUser
from app.schemas import ApiResponse, BoardCreateRequest, BoardResponse, BoardUpdateRequest
from app.utils.request_context import get_request_id

router = APIRouter(prefix="/boards", tags=["boards"])


@router.get("", response_model=ApiResponse[list[BoardResponse]])
async def list_boards(
    request: Request, current_user: CurrentUser, service: BoardServiceDep
) -> ApiResponse[list[BoardResponse]]:
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
