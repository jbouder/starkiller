"""Pytest fixtures for Starkiller API tests."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import Settings
from core.database import get_db_session
from main import app
from models import Base

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override the database dependency for testing."""

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    return _override_get_db


@pytest.fixture
def client(override_get_db) -> Generator[TestClient, None, None]:
    """Create a test client with database override."""
    app.dependency_overrides[get_db_session] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with database override."""
    app.dependency_overrides[get_db_session] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        environment="development",
        debug=True,
        database_url=TEST_DATABASE_URL,
        anthropic_api_key="test-api-key",
    )


@pytest.fixture
def sample_data_source_config() -> dict[str, Any]:
    """Sample data source configuration for testing."""
    return {
        "name": "Test Data Source",
        "description": "A test data source",
        "source_type": "csv",
        "connection_config": {"file_path": "/tmp/test.csv"},
    }


@pytest.fixture
def sample_query_request() -> dict[str, Any]:
    """Sample query request for testing."""
    return {
        "query": "Show me the total sales by month",
        "data_source_id": None,
    }
