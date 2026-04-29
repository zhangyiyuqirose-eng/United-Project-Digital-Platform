"""Tests for audit API endpoints."""

import pytest
from datetime import datetime, timezone

from app.models.audit.models import AuditLogEntry


def _make_entry(entry_id, user_id="u1", action="LOGIN", resource_type="SYSTEM",
                resource_id=None, timestamp=None):
    return AuditLogEntry(
        entry_id=entry_id,
        audit_id=f"audit-{entry_id}",
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details="test details",
        ip_address="127.0.0.1",
        timestamp=timestamp or datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_list_audit_logs_empty(client):
    resp = await client.get("/api/audit/logs")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert data["data"]["total"] == 0
    assert data["data"]["records"] == []


@pytest.mark.asyncio
async def test_list_audit_logs_pagination(client, db_session):
    for i in range(25):
        db_session.add(_make_entry(f"e-{i}"))
    await db_session.flush()

    resp = await client.get("/api/audit/logs", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert data["data"]["total"] == 25
    assert len(data["data"]["records"]) == 10
    assert data["data"]["page"] == 1
    assert data["data"]["size"] == 10


@pytest.mark.asyncio
async def test_list_audit_logs_filter_by_user_id(client, db_session):
    db_session.add(_make_entry("e-u1", user_id="user-a"))
    db_session.add(_make_entry("e-u2", user_id="user-b"))
    db_session.add(_make_entry("e-u3", user_id="user-a"))
    await db_session.flush()

    resp = await client.get("/api/audit/logs", params={"user_id": "user-a"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["total"] == 2
    for r in data["data"]["records"]:
        assert r["userId"] == "user-a"


@pytest.mark.asyncio
async def test_list_audit_logs_filter_by_action(client, db_session):
    db_session.add(_make_entry("e-a1", action="LOGIN"))
    db_session.add(_make_entry("e-a2", action="LOGOUT"))
    db_session.add(_make_entry("e-a3", action="LOGIN"))
    await db_session.flush()

    resp = await client.get("/api/audit/logs", params={"action": "LOGIN"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["total"] == 2
    for r in data["data"]["records"]:
        assert r["action"] == "LOGIN"


@pytest.mark.asyncio
async def test_list_audit_logs_filter_by_resource_type(client, db_session):
    db_session.add(_make_entry("e-r1", resource_type="USER"))
    db_session.add(_make_entry("e-r2", resource_type="PROJECT"))
    await db_session.flush()

    resp = await client.get("/api/audit/logs", params={"resource_type": "USER"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["total"] == 1
    assert data["data"]["records"][0]["resourceType"] == "USER"


@pytest.mark.asyncio
async def test_export_audit_logs(client, db_session):
    db_session.add(_make_entry("exp-1", user_id="exp-user"))
    db_session.add(_make_entry("exp-2", user_id="other-user"))
    await db_session.flush()

    resp = await client.get("/api/audit/logs/export", params={"user_id": "exp-user"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert len(data["data"]) == 1
    assert data["data"][0]["userId"] == "exp-user"


@pytest.mark.asyncio
async def test_export_audit_logs_filter_by_action(client, db_session):
    db_session.add(_make_entry("exp-a1", action="DELETE"))
    db_session.add(_make_entry("exp-a2", action="CREATE"))
    await db_session.flush()

    resp = await client.get("/api/audit/logs/export", params={"action": "DELETE"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["action"] == "DELETE"


@pytest.mark.asyncio
async def test_export_audit_logs_unfiltered(client, db_session):
    for i in range(5):
        db_session.add(_make_entry(f"exp-all-{i}"))
    await db_session.flush()

    resp = await client.get("/api/audit/logs/export")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert len(data["data"]) == 5


@pytest.mark.asyncio
async def test_audit_summary_empty(client):
    resp = await client.get("/api/audit/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert data["data"]["totalEntries"] == 0
    assert data["data"]["todayEntries"] == 0
    assert data["data"]["actionBreakdown"] == []


@pytest.mark.asyncio
async def test_audit_summary_with_data(client, db_session):
    db_session.add(_make_entry("sum-1", action="LOGIN"))
    db_session.add(_make_entry("sum-2", action="LOGIN"))
    db_session.add(_make_entry("sum-3", action="DELETE"))
    await db_session.flush()

    resp = await client.get("/api/audit/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert data["data"]["totalEntries"] == 3
    assert data["data"]["todayEntries"] == 3
    breakdown = data["data"]["actionBreakdown"]
    login_entry = next(b for b in breakdown if b["action"] == "LOGIN")
    assert login_entry["count"] == 2
    delete_entry = next(b for b in breakdown if b["action"] == "DELETE")
    assert delete_entry["count"] == 1


@pytest.mark.asyncio
async def test_recent_operations_default_limit(client, db_session):
    for i in range(60):
        db_session.add(_make_entry(f"recent-{i}"))
    await db_session.flush()

    resp = await client.get("/api/audit/recent")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert len(data["data"]) == 50


@pytest.mark.asyncio
async def test_recent_operations_custom_limit(client, db_session):
    for i in range(20):
        db_session.add(_make_entry(f"recent-lim-{i}"))
    await db_session.flush()

    resp = await client.get("/api/audit/recent", params={"limit": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["data"]) == 5


@pytest.mark.asyncio
async def test_recent_operations_response_fields(client, db_session):
    db_session.add(_make_entry("recent-fields", user_id="test-user", action="CREATE",
                               resource_type="PROJECT", resource_id="proj-1"))
    await db_session.flush()

    resp = await client.get("/api/audit/recent", params={"limit": 1})
    assert resp.status_code == 200
    data = resp.json()
    record = data["data"][0]
    assert "entryId" in record
    assert "userId" in record
    assert "action" in record
    assert "resourceType" in record
    assert "resourceId" in record
    assert "timestamp" in record
    assert record["userId"] == "test-user"
    assert record["action"] == "CREATE"
