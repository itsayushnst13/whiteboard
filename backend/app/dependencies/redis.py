from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.db.redis import get_redis_client

RedisClient = Annotated[Redis, Depends(get_redis_client)]
