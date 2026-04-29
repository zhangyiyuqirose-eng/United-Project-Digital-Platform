"""Integration tests for cost service extended endpoints."""

import pytest

from app.models.cost.models import CostSettlement
from app.models.project.models import Project


# ── Cost Settlement ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_settlement(client, db_session):
    db_session.add(Project(
        project_id="proj-cost-1",
        project_name="成本结算项目",
        project_code="COST-001",
        status="active",
    ))
    await db_session.flush()

    resp = await client.post("/api/cost/settlements", json={
        "project_id": "proj-cost-1",
        "settlement_amount": 250000.0,
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert "settlementId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_list_settlements(client, db_session):
    db_session.add(CostSettlement(
        settlement_id="set-list-1",
        project_id="proj-cost-2",
        settlement_amount=100000.0,
        status="pending",
    ))
    await db_session.flush()

    resp = await client.get("/api/cost/settlements", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_approve_settlement(client, db_session):
    db_session.add(CostSettlement(
        settlement_id="set-approve-1",
        project_id="proj-cost-3",
        settlement_amount=150000.0,
        status="pending",
    ))
    await db_session.flush()

    resp = await client.post("/api/cost/settlements/set-approve-1/approve")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_reject_settlement(client, db_session):
    db_session.add(CostSettlement(
        settlement_id="set-reject-cost-1",
        project_id="proj-cost-4",
        settlement_amount=80000.0,
        status="pending",
    ))
    await db_session.flush()

    resp = await client.post("/api/cost/settlements/set-reject-cost-1/reject", json={
        "reason": "金额不符",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


# ── Cost Trend ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cost_trend(client, db_session):
    db_session.add(Project(
        project_id="proj-trend-1",
        project_name="趋势分析项目",
        project_code="TREND-001",
        status="active",
        budget=200000.0,
    ))
    await db_session.flush()

    resp = await client.get("/api/cost/trend/proj-trend-1")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


# ── Budget Execution ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_budget_execution(client, db_session):
    db_session.add(Project(
        project_id="proj-budget-exec-1",
        project_name="预算执行项目",
        project_code="BUDGET-001",
        status="active",
        budget=500000.0,
    ))
    await db_session.flush()

    resp = await client.get("/api/cost/budget-execution", params={
        "project_id": "proj-budget-exec-1",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
