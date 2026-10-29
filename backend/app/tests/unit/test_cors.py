from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.core.middleware import register_middleware

PROD_ORIGIN = "https://syncboard.vercel.app"


def _app() -> FastAPI:
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://u:p@localhost:5432/db",
        REDIS_URL="redis://localhost:6379/0",
        JWT_SECRET_KEY="x",
        BACKEND_CORS_ORIGINS=f"{PROD_ORIGIN}/",
    )
    app = FastAPI()
    register_middleware(app, settings)

    @app.post("/auth/login")
    async def login() -> dict[str, bool]:
        return {"ok": True}

    return app


async def _preflight(origin: str) -> tuple[int, dict[str, str]]:
    transport = ASGITransport(app=_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.options(
            "/auth/login",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type,authorization",
            },
        )
    return response.status_code, dict(response.headers)


async def test_preflight_allows_configured_production_origin() -> None:
    status, headers = await _preflight(PROD_ORIGIN)
    assert status == 200
    assert headers["access-control-allow-origin"] == PROD_ORIGIN


async def test_preflight_rejects_disallowed_origin() -> None:
    status, headers = await _preflight("https://evil.example.com")
    assert status == 400
    assert "access-control-allow-origin" not in headers
