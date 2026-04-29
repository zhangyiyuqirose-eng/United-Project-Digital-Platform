"""Extended tests for auth API: password policy, account lock/unlock, SSO callback."""

import pytest
from datetime import datetime, timezone

from app.core.security import hash_password
from app.models.auth.models import User


@pytest.mark.asyncio
async def test_get_password_policy(client):
    resp = await client.get("/api/auth/password-policy")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    policy = data["data"]
    assert policy["minLength"] == 8
    assert policy["maxLength"] == 32
    assert policy["requireUppercase"] is True
    assert policy["requireLowercase"] is True
    assert policy["requireDigit"] is True
    assert policy["requireSpecialChar"] is True
    assert policy["historyCount"] == 5
    assert policy["expiryDays"] == 90
    assert policy["maxFailedAttempts"] == 5
    assert policy["lockoutDurationMinutes"] == 30


@pytest.mark.asyncio
async def test_lock_account_success(client, db_session):
    user = User(
        user_id="lock-test-user-1",
        username="lockuser",
        password=hash_password("TestPass123!"),
        name="Lock User",
        status=1,
    )
    db_session.add(user)
    await db_session.flush()

    resp = await client.post("/api/auth/account/lock/lock-test-user-1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"

    # Verify status changed in DB
    from sqlalchemy import select
    stmt = select(User).where(User.user_id == "lock-test-user-1")
    updated = (await db_session.execute(stmt)).scalar_one()
    assert updated.status == 0


@pytest.mark.asyncio
async def test_lock_account_not_found(client):
    resp = await client.post("/api/auth/account/lock/nonexistent-user")
    assert resp.status_code == 400
    data = resp.json()
    assert data["code"] == "USER_NOT_FOUND"


@pytest.mark.asyncio
async def test_unlock_account_success(client, db_session):
    user = User(
        user_id="unlock-test-user-1",
        username="unlockuser",
        password=hash_password("TestPass123!"),
        name="Unlock User",
        status=0,
    )
    db_session.add(user)
    await db_session.flush()

    resp = await client.post("/api/auth/account/unlock/unlock-test-user-1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"

    from sqlalchemy import select
    stmt = select(User).where(User.user_id == "unlock-test-user-1")
    updated = (await db_session.execute(stmt)).scalar_one()
    assert updated.status == 1


@pytest.mark.asyncio
async def test_unlock_account_not_found(client):
    resp = await client.post("/api/auth/account/unlock/nonexistent-user")
    assert resp.status_code == 400
    data = resp.json()
    assert data["code"] == "USER_NOT_FOUND"


@pytest.mark.asyncio
async def test_sso_callback_no_ticket(client):
    resp = await client.get("/api/auth/sso/callback")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_sso_callback_returns_sso_not_configured(client):
    resp = await client.get("/api/auth/sso/callback", params={"ticket": "some-ticket"})
    assert resp.status_code == 400
    data = resp.json()
    assert data["code"] == "SSO_NOT_CONFIGURED"


@pytest.mark.asyncio
async def test_change_password_success(client, db_session):
    user = User(
        user_id="cp-test-user-1",
        username="cpuser",
        password=hash_password("OldPass123!"),
        name="Change Password User",
        status=1,
        password_changed_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.flush()

    from app.core.security import create_token
    token = create_token("cp-test-user-1", {"role": "user", "username": "cpuser"})

    resp = await client.post(
        "/api/auth/change-password",
        json={"old_password": "OldPass123!", "new_password": "NewPass456!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_change_password_wrong_old_password(client, db_session):
    user = User(
        user_id="cp-test-user-2",
        username="cpuser2",
        password=hash_password("CorrectOld!"),
        name="CP User 2",
        status=1,
    )
    db_session.add(user)
    await db_session.flush()

    from app.core.security import create_token
    token = create_token("cp-test-user-2", {"role": "user", "username": "cpuser2"})

    resp = await client.post(
        "/api/auth/change-password",
        json={"old_password": "WrongOld!", "new_password": "NewPass456!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_change_password_too_short(client, db_session):
    user = User(
        user_id="cp-test-user-3",
        username="cpuser3",
        password=hash_password("OldPass123!"),
        name="CP User 3",
        status=1,
    )
    db_session.add(user)
    await db_session.flush()

    from app.core.security import create_token
    token = create_token("cp-test-user-3", {"role": "user", "username": "cpuser3"})

    resp = await client.post(
        "/api/auth/change-password",
        json={"old_password": "OldPass123!", "new_password": "short"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
