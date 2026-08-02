import pytest
from httpx import AsyncClient

from app.schemas.health import ComponentHealth
from app.services import health_service as health_service_module


async def _healthy_db() -> ComponentHealth:
    return ComponentHealth(name="postgres", healthy=True)


async def _healthy_redis() -> ComponentHealth:
    return ComponentHealth(name="redis", healthy=True)


async def _unhealthy_redis() -> ComponentHealth:
    return ComponentHealth(name="redis", healthy=False)


async def test_root_returns_service_info(client: AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["name"] == "SyncBoard"
    assert response.headers["X-Request-ID"]


async def test_liveness_never_checks_dependencies(client: AsyncClient) -> None:
    response = await client.get("/liveness")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "alive"


async def test_readiness_returns_ready_when_dependencies_healthy(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(health_service_module, "check_database", _healthy_db)
    monkeypatch.setattr(health_service_module, "check_redis", _healthy_redis)

    response = await client.get("/readiness")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "ready"
    assert {check["name"] for check in body["data"]["checks"]} == {"postgres", "redis"}


async def test_readiness_returns_503_when_a_dependency_is_unhealthy(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(health_service_module, "check_database", _healthy_db)
    monkeypatch.setattr(health_service_module, "check_redis", _unhealthy_redis)

    response = await client.get("/readiness")

    assert response.status_code == 503
    assert response.json()["data"]["status"] == "not_ready"


async def test_health_reports_version_and_environment(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(health_service_module, "check_database", _healthy_db)
    monkeypatch.setattr(health_service_module, "check_redis", _healthy_redis)

    response = await client.get("/health")

    body = response.json()
    assert body["data"]["status"] == "healthy"
    assert body["data"]["environment"] == "test"
