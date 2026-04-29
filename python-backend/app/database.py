"""Async database session management."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# SQLite doesn't support pool_size/max_overflow
is_sqlite = "sqlite" in settings.database_url

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    **({} if is_sqlite else {"pool_size": 20, "max_overflow": 10, "pool_pre_ping": True}),
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
