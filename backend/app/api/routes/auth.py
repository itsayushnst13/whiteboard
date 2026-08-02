from fastapi import APIRouter, Request

from app.dependencies import AuthServiceDep, CurrentUser, SettingsDep
from app.schemas import ApiResponse, LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.utils.request_context import get_request_id

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=ApiResponse[TokenResponse])
async def register(
    request: Request,
    payload: RegisterRequest,
    service: AuthServiceDep,
    settings: SettingsDep,
) -> ApiResponse[TokenResponse]:
    data = await service.register(payload, settings)
    return ApiResponse.ok(data, request_id=get_request_id(request))


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(
    request: Request,
    payload: LoginRequest,
    service: AuthServiceDep,
    settings: SettingsDep,
) -> ApiResponse[TokenResponse]:
    data = await service.login(payload, settings)
    return ApiResponse.ok(data, request_id=get_request_id(request))


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_me(request: Request, current_user: CurrentUser) -> ApiResponse[UserResponse]:
    data = UserResponse(
        id=current_user.id, email=current_user.email, display_name=current_user.display_name
    )
    return ApiResponse.ok(data, request_id=get_request_id(request))
