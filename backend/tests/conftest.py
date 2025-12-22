"""Shared test fixtures and configuration."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.config import Settings, get_settings
from src.db.database import Base, get_db
from src.main import create_app


# Test database URL (SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


def get_test_settings() -> Settings:
    """Create test settings with test values."""
    return Settings(
        openai_api_key="test-openai-key",
        qdrant_url="http://localhost:6333",
        qdrant_api_key="test-qdrant-key",
        database_url=TEST_DATABASE_URL,
        cors_origins="http://localhost:3000",
        confidence_threshold=0.7,
        qdrant_collection_name="test_book_chunks",
    )


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Provide test settings."""
    return get_test_settings()


@pytest_asyncio.fixture
async def async_engine():
    """Create async test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for tests."""
    async_session_factory = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_factory() as session:
        yield session


@pytest.fixture
def app(test_settings):
    """Create FastAPI test application."""
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: test_settings
    return app


@pytest.fixture
def client(app) -> Generator[TestClient, None, None]:
    """Create synchronous test client."""
    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture
async def async_client(app, db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client with database session."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Create mock OpenAI client."""
    mock = MagicMock()
    mock.create_embedding = AsyncMock(return_value=[0.1] * 1536)
    mock.create_chat_completion = AsyncMock(return_value={
        "content": "This is a test response based on the book content.",
        "model": "gpt-4o-mini",
    })
    return mock


@pytest.fixture
def mock_qdrant_client() -> MagicMock:
    """Create mock Qdrant client."""
    mock = MagicMock()
    mock.search = AsyncMock(return_value=[
        {
            "id": "chunk-1",
            "score": 0.85,
            "payload": {
                "text": "This is relevant book content about the topic.",
                "chapter": "Chapter 1",
                "section": "Introduction",
                "page": 1,
            },
        },
        {
            "id": "chunk-2",
            "score": 0.75,
            "payload": {
                "text": "Additional context from the book.",
                "chapter": "Chapter 1",
                "section": "Overview",
                "page": 2,
            },
        },
    ])
    return mock


@pytest.fixture
def sample_book_chunks() -> list[dict[str, Any]]:
    """Provide sample book chunks for testing."""
    return [
        {
            "id": "chunk-1",
            "text": "Python is a high-level programming language known for its readability.",
            "chapter": "Chapter 1",
            "section": "Introduction to Python",
            "page": 1,
        },
        {
            "id": "chunk-2",
            "text": "Variables in Python are dynamically typed.",
            "chapter": "Chapter 2",
            "section": "Variables and Types",
            "page": 15,
        },
        {
            "id": "chunk-3",
            "text": "Functions are defined using the def keyword.",
            "chapter": "Chapter 3",
            "section": "Functions",
            "page": 45,
        },
    ]


@pytest.fixture
def sample_conversation_id() -> str:
    """Provide sample conversation UUID."""
    return "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def sample_chat_request() -> dict[str, Any]:
    """Provide sample chat request payload."""
    return {
        "message": "What is Python?",
        "conversation_id": None,
    }


@pytest.fixture
def sample_chat_response() -> dict[str, Any]:
    """Provide expected chat response structure."""
    return {
        "message": "Python is a high-level programming language known for its readability.",
        "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
        "sources": [
            {
                "chapter": "Chapter 1",
                "section": "Introduction to Python",
                "page": 1,
                "relevance": 0.85,
            }
        ],
    }
