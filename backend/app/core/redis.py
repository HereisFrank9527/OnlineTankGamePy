from typing import Optional

from redis import asyncio as aioredis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

redis_client: Optional[aioredis.Redis] = None


async def init_redis() -> None:
    global redis_client
    logger.info("Initializing Redis connection...")
    try:
        redis_client = aioredis.from_url(
            str(settings.REDIS_URL),
            encoding="utf-8",
            decode_responses=True,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
        )
        await redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise


async def close_redis() -> None:
    global redis_client
    if redis_client:
        logger.info("Closing Redis connection...")
        await redis_client.close()
        redis_client = None
        logger.info("Redis connection closed")


def get_redis() -> aioredis.Redis:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized")
    return redis_client
