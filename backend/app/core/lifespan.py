import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.db.postgres import get_engine
from app.db.redis import get_redis_client
from app.logging.config import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    setup_logging(settings)
    logger.info(
        "Starting %s", settings.PROJECT_NAME, extra={"environment": settings.ENVIRONMENT.value}
    )

    yield

    logger.info("Shutting down %s", settings.PROJECT_NAME)
    await get_engine().dispose()
    await get_redis_client().aclose()
