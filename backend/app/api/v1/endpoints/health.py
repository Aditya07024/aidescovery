from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis_client

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Liveness probe endpoint.
    """
    return {"status": "ok", "service": "universal-ai-discovery-engine"}


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness probe checking database and redis connectivity.
    """
    db_ok = False
    redis_ok = False

    # Check Database
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    # Check Redis
    try:
        rc = await get_redis_client()
        if rc and await rc.ping():
            redis_ok = True
    except Exception:
        redis_ok = False

    is_ready = db_ok  # Service functions even in fallback mode if Redis is temporarily offline

    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "database": "connected" if db_ok else "disconnected",
            "redis": "connected" if redis_ok else "unavailable_fallback_active",
        },
    )
