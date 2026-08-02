from fastapi import APIRouter, Request, Response, status

from app.dependencies import HealthServiceDep, SettingsDep
from app.schemas import ApiResponse, HealthResponse, LivenessResponse, ReadinessResponse
from app.utils.request_context import get_request_id

router = APIRouter(tags=["health"])


@router.get("/health", response_model=ApiResponse[HealthResponse])
async def get_health(
    request: Request, settings: SettingsDep, service: HealthServiceDep
) -> ApiResponse[HealthResponse]:
    data = await service.get_health(settings)
    return ApiResponse.ok(data, request_id=get_request_id(request))


@router.get("/liveness", response_model=ApiResponse[LivenessResponse])
async def get_liveness(request: Request) -> ApiResponse[LivenessResponse]:
    """Confirms the process is up and serving requests. Never checks
    Postgres or Redis — an orchestrator uses this to decide whether to
    restart the container, and a slow dependency shouldn't trigger that."""
    return ApiResponse.ok(LivenessResponse(), request_id=get_request_id(request))


@router.get("/readiness", response_model=ApiResponse[ReadinessResponse])
async def get_readiness(
    request: Request, response: Response, service: HealthServiceDep
) -> ApiResponse[ReadinessResponse]:
    """Confirms Postgres and Redis are reachable. An orchestrator uses
    this to decide whether to route traffic to this instance."""
    data = await service.get_readiness()
    if data.status == "not_ready":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ApiResponse.ok(data, request_id=get_request_id(request))
