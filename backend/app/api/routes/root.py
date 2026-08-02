from fastapi import APIRouter, Request

from app.dependencies import SettingsDep
from app.schemas import ApiResponse, ServiceInfo
from app.utils.request_context import get_request_id

router = APIRouter(tags=["root"])


@router.get("/", response_model=ApiResponse[ServiceInfo])
async def read_root(request: Request, settings: SettingsDep) -> ApiResponse[ServiceInfo]:
    data = ServiceInfo(
        name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT.value,
        docs_url=None if settings.is_production else "/docs",
    )
    return ApiResponse.ok(data, request_id=get_request_id(request))
