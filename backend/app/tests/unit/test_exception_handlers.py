from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI, Query
from httpx import ASGITransport, AsyncClient

from app.exceptions import NotFoundError, register_exception_handlers
from app.middleware import RequestContextMiddleware


def _build_app() -> FastAPI:
    """A minimal app isolated from the real route tree, just for
    exercising the exception-handling plumbing."""
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)
    register_exception_handlers(app)

    @app.get("/boom/not-found")
    async def boom_not_found() -> None:
        raise NotFoundError("thing missing")

    @app.get("/boom/unhandled")
    async def boom_unhandled() -> None:
        raise RuntimeError("kaboom")

    @app.get("/needs-count")
    async def needs_count(count: int = Query(...)) -> dict[str, int]:
        return {"count": count}

    return app


@pytest.fixture
async def exc_client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=_build_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_app_exception_returns_error_envelope(exc_client: AsyncClient) -> None:
    response = await exc_client.get("/boom/not-found")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"] == "thing missing"


async def test_unknown_route_returns_error_envelope(exc_client: AsyncClient) -> None:
    response = await exc_client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "HTTP_ERROR"


async def test_unhandled_exception_returns_500_without_leaking_details(
    exc_client: AsyncClient,
) -> None:
    response = await exc_client.get("/boom/unhandled")

    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "INTERNAL_ERROR"
    assert "kaboom" not in response.text


async def test_validation_error_returns_field_details(exc_client: AsyncClient) -> None:
    response = await exc_client.get("/needs-count")

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["details"][0]["field"] == "query.count"
