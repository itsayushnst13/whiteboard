from typing import Literal

from pydantic import BaseModel


class ComponentHealth(BaseModel):
    name: str
    healthy: bool


class LivenessResponse(BaseModel):
    """Process-alive check only. Never touches Postgres or Redis, so it
    can't report unhealthy just because a dependency is down."""

    status: Literal["alive"] = "alive"


class ReadinessResponse(BaseModel):
    """Whether the app can currently serve traffic that depends on
    Postgres and Redis."""

    status: Literal["ready", "not_ready"]
    checks: list[ComponentHealth]


class HealthResponse(BaseModel):
    """Human-facing snapshot combining service metadata with dependency
    status — meant for dashboards, not load balancer probes."""

    status: Literal["healthy", "unhealthy"]
    version: str
    environment: str
    checks: list[ComponentHealth]
