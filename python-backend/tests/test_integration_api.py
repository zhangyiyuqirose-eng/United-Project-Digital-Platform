"""Integration tests for integration service API."""

import pytest


# ── HR Integration ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_hr_employee_query(client):
    resp = await client.get("/api/integration/hr/employee/EMP-001")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "employeeId" in data
    assert "name" in data


@pytest.mark.asyncio
async def test_hr_org_sync(client):
    resp = await client.post("/api/integration/hr/sync-org")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "synced" in data


# ── Finance Integration ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_finance_push_settlement(client):
    resp = await client.post("/api/integration/finance/settlement", json={
        "projectId": "proj-fin-1",
        "amount": 50000.0,
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "settlementId" in data


@pytest.mark.asyncio
async def test_finance_payment_query(client):
    resp = await client.get("/api/integration/finance/payment/SETTLE-001")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "status" in data


# ── DevOps Integration ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_devops_build_status(client):
    resp = await client.get("/api/integration/devops/build/proj-dev-1")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "buildNumber" in data


@pytest.mark.asyncio
async def test_devops_test_results(client):
    resp = await client.get("/api/integration/devops/test/proj-dev-1")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "passed" in data
