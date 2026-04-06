from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import get_settings
from app.middleware.rate_limit import RateLimitMiddleware
from app.utils.response import AppException, error_response
from app.services.task_service import expire_points, penalize_incomplete

settings = get_settings()
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler.add_job(expire_points, "cron", hour=0, minute=5, id="expire_points")
    scheduler.add_job(penalize_incomplete, "cron", hour=23, minute=55, id="penalize_incomplete")
    scheduler.start()
    logger.info("Scheduler started")
    yield
    # Shutdown
    scheduler.shutdown()
    logger.info("Scheduler stopped")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimitMiddleware)


# Global exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(code=exc.code, message=exc.message),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=error_response(code=10000, message="服务器内部错误"),
    )


# Health check
@app.get("/health")
def health():
    """Health check: DB + Redis"""
    from app.database import engine
    from app.redis_client import get_redis

    db_ok = False
    redis_ok = False

    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        logger.error(f"DB health check failed: {e}")

    try:
        r = get_redis()
        r.ping()
        redis_ok = True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")

    status = "healthy" if (db_ok and redis_ok) else "unhealthy"
    return {
        "status": status,
        "database": "ok" if db_ok else "error",
        "redis": "ok" if redis_ok else "error",
    }


# Register routers
from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.homework import router as homework_router
from app.api.points import router as points_router
from app.api.reward import router as reward_router
from app.api.exchange import router as exchange_router
from app.api.admin import router as admin_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(homework_router, prefix="/api/v1")
app.include_router(points_router, prefix="/api/v1")
app.include_router(reward_router, prefix="/api/v1")
app.include_router(exchange_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
