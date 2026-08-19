import logging
from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# Determine if async database URL requires sqlite or postgresql
database_url = settings.DATABASE_URL
sync_database_url = settings.SYNC_DATABASE_URL

# For SQLite async compatibility
if database_url.startswith("sqlite://"):
    database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")

# Async Engine & Session
async_engine = create_async_engine(
    database_url,
    echo=settings.LOG_LEVEL.upper() == "DEBUG",
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Sync Engine for Alembic migrations & background tasks if needed
sync_engine = create_engine(
    sync_database_url,
    echo=settings.LOG_LEVEL.upper() == "DEBUG",
)

SyncSessionLocal = sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
