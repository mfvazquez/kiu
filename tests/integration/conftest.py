import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from app.main import app

TEST_API_BASE_URL = "http://test"


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_cache():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield


@pytest_asyncio.fixture(scope="session")
async def test_app():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=TEST_API_BASE_URL
    ) as client:
        yield client
