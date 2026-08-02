from fastapi import FastAPI

from app.api.router import api_router
from app.config import get_settings
from app.core.lifespan import lifespan
from app.core.middleware import register_middleware
from app.exceptions import register_exception_handlers


def create_app() -> FastAPI:
    """Application factory — keeps `main.py` a one-line entrypoint and
    lets tests build isolated app instances if ever needed."""
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        openapi_url=None if settings.is_production else "/openapi.json",
        lifespan=lifespan,
    )

    register_middleware(app, settings)
    register_exception_handlers(app)
    app.include_router(api_router)

    return app
