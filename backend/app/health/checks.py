from app.db.postgres import ping_database
from app.db.redis import ping_redis
from app.schemas.health import ComponentHealth


async def check_database() -> ComponentHealth:
    return ComponentHealth(name="postgres", healthy=await ping_database())


async def check_redis() -> ComponentHealth:
    return ComponentHealth(name="redis", healthy=await ping_redis())
