from __future__ import annotations

import redis
from app.config import get_settings

settings = get_settings()

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD or None,
    db=settings.REDIS_DB,
    decode_responses=True,
    socket_connect_timeout=5,
    retry_on_timeout=True,
)


def get_redis() -> redis.Redis:
    return redis_client
