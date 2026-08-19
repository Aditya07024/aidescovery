import asyncio
import os
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["DEFAULT_AI_PROVIDER"] = "mock"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_aidiscovery.db"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///./test_aidiscovery.db"

from app.core.database import Base, async_engine, get_db
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    if os.path.exists("./test_aidiscovery.db"):
        os.remove("./test_aidiscovery.db")


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
