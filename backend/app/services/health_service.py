import asyncio

from app.config import Settings
from app.health.checks import check_database, check_redis
from app.schemas.health import ComponentHealth, HealthResponse, ReadinessResponse


class HealthService:
    """Composes the individual dependency checks in `app.health` into the
    response shapes the API exposes. Kept separate from the route layer so
    the composition logic is unit-testable without spinning up FastAPI."""

    async def _run_checks(self) -> list[ComponentHealth]:
        database, redis = await asyncio.gather(check_database(), check_redis())
        return [database, redis]

    async def get_readiness(self) -> ReadinessResponse:
        checks = await self._run_checks()
        status = "ready" if all(check.healthy for check in checks) else "not_ready"
        return ReadinessResponse(status=status, checks=checks)

    async def get_health(self, settings: Settings) -> HealthResponse:
        checks = await self._run_checks()
        status = "healthy" if all(check.healthy for check in checks) else "unhealthy"
        return HealthResponse(
            status=status,
            version=settings.VERSION,
            environment=settings.ENVIRONMENT.value,
            checks=checks,
        )
