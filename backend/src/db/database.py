"""SQLAlchemy database setup and session management."""

from typing import AsyncGenerator

from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


settings = get_settings()

# Parse and modify URL for asyncpg compatibility
url = make_url(settings.database_url)
connect_args = {
    # Disable prepared statement caching to avoid InvalidCachedStatementError
    "prepared_statement_cache_size": 0,
}

if url.drivername == "postgresql+asyncpg":
    # Remove incompatible query parameters for asyncpg
    query = dict(url.query)
    if "sslmode" in query:
        del query["sslmode"]
        # Map sslmode=require to ssl="require" for asyncpg
        connect_args["ssl"] = "require"
    if "channel_binding" in query:
        del query["channel_binding"]

    # Update URL without the removed query params
    url = url._replace(query=query)

# Create async engine
engine = create_async_engine(
    url,
    connect_args=connect_args,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    # Handle schema changes gracefully
    pool_recycle=300,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
