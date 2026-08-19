import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.database import Base, async_engine, sync_engine
from app.core.redis import close_redis_client, get_redis_client

# Configure Logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Universal AI Discovery Platform Backend...")
    
    # Initialize database tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized.")

    # Initialize Redis connection
    await get_redis_client()

    yield

    logger.info("Shutting down backend resources...")
    await close_redis_client()
    await async_engine.dispose()


app = FastAPI(
    title="Universal AI Discovery Platform API",
    description="AI-powered entity discovery, normalization, deduplication, and qualification engine.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler matching Section 42 requirement
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled Exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred during request execution.",
                "request_id": str(request.headers.get("X-Request-ID", "unknown")),
            }
        },
    )


# Mount API v1 router under /api/v1
app.include_router(api_v1_router, prefix="/api")

# Top level root endpoints
@app.get("/")
async def root():
    return {
        "title": "Universal AI Discovery Platform Engine",
        "status": "operational",
        "docs": "/docs",
        "api_v1": "/api/v1",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    return {"status": "ready"}
