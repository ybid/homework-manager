from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.redis_client import get_redis
from app.config import get_settings

settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple sliding-window rate limiter using Redis."""

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"

        try:
            r = get_redis()
            current = r.get(key)
            if current is not None and int(current) >= settings.RATE_LIMIT_PER_MINUTE:
                return JSONResponse(
                    status_code=429,
                    content={
                        "code": 10029,
                        "message": "请求过于频繁，请稍后再试",
                        "data": None,
                    },
                )
            pipe = r.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60)
            pipe.execute()
        except Exception:
            # If Redis is down, allow the request through
            pass

        response = await call_next(request)
        return response
