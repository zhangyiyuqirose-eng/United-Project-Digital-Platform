"""Test configuration: fixtures for DB, test client, and async event loop."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import create_token
from app.database import get_db
from app.main import create_app
from app.models.base import Base

# Import all models so Base.metadata knows about them
import app.models.auth  # noqa: F401
import app.models.system  # noqa: F401
import app.models.project  # noqa: F401
import app.models.business  # noqa: F401
import app.models.cost  # noqa: F401
import app.models.resource  # noqa: F401
import app.models.timesheet  # noqa: F401
import app.models.knowledge  # noqa: F401
import app.models.workflow  # noqa: F401
import app.models.notify  # noqa: F401
import app.models.quality  # noqa: F401
import app.models.file  # noqa: F401
import app.models.audit  # noqa: F401
import app.models.report  # noqa: F401

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSession() as session:
        yield session
        await session.rollback()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Generate a test JWT token for authenticated endpoints
    test_token = create_token(user_id="test-user", claims={"role": "admin", "username": "testadmin"})

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {test_token}"},
    ) as ac:
        yield ac


@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
