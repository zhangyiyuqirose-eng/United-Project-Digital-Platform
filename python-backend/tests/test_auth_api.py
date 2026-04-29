"""Integration tests for auth API endpoints."""

import pytest

from app.core.security import hash_password
from app.models.auth.models import User


@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_login_success(client, db_session):
    user = User(
        user_id="test-user-1",
        username="testuser",
        password=hash_password("TestPass123!"),
        name="Test User",
        status=1,
    )
    db_session.add(user)
    await db_session.flush()

    resp = await client.post("/api/auth/login", json={"username": "testuser", "password": "TestPass123!"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert "accessToken" in data["data"]
    assert "refreshToken" in data["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(client, db_session):
    user = User(
        user_id="test-user-2",
        username="testuser2",
        password=hash_password("CorrectPass!"),
        name="Test User 2",
        status=1,
    )
    db_session.add(user)
    await db_session.flush()

    resp = await client.post("/api/auth/login", json={"username": "testuser2", "password": "WrongPass!"})
    assert resp.status_code == 422  # ValidationError


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    resp = await client.post("/api/auth/login", json={"username": "nobody", "password": "pass"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_disabled_account(client, db_session):
    user = User(
        user_id="test-user-3",
        username="disabled",
        password=hash_password("TestPass123!"),
        name="Disabled User",
        status=0,  # disabled
    )
    db_session.add(user)
    await db_session.flush()

    resp = await client.post("/api/auth/login", json={"username": "disabled", "password": "TestPass123!"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_logout(client):
    resp = await client.post("/api/auth/logout")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_refresh_invalid_token(client):
    resp = await client.post("/api/auth/refresh", headers={"X-Refresh-Token": "invalid"})
    assert resp.status_code == 401
