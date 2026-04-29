"""Comprehensive tests for cost API endpoints."""

import pytest
from datetime import date, datetime, timezone
from decimal import Decimal

from app.models.cost.models import Budget, Cost, CostAlert, CostSettlement, ExpenseReimbursement
from app.models.project.models import Project


# ── Budget CRUD + Approve ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_budget(client, db_session):
    """Create a new budget record."""
    resp = await client.post("/api/cost/budgets", json={
        "project_id": "proj-budget-1",
        "budget_year": 2026,
        "total_budget": 100000.0,
        "labor_budget": 40000.0,
        "outsource_budget": 30000.0,
        "procurement_budget": 20000.0,
        "other_budget": 10000.0,
        "status": "DRAFT",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SUCCESS"
    assert "budgetId" in body["data"]


@pytest.mark.asyncio
async def test_list_budgets_empty(client, db_session):
    """List budgets when none exist returns empty records."""
    resp = await client.get("/api/cost/budgets", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SUCCESS"
    assert body["data"]["total"] == 0
    assert body["data"]["records"] == []


@pytest.mark.asyncio
async def test_list_budgets_with_data(client, db_session):
    """List budgets filters by project_id and status."""
    db_session.add(Budget(
        budget_id="bud-list-1",
        project_id="proj-budget-2",
        budget_year=2026,
        total_budget=Decimal("200000.00"),
        status="DRAFT",
    ))
    db_session.add(Budget(
        budget_id="bud-list-2",
        project_id="proj-budget-3",
        budget_year=2026,
        total_budget=Decimal("300000.00"),
        status="APPROVED",
    ))
    await db_session.flush()

    resp = await client.get("/api/cost/budgets", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 2

    resp = await client.get("/api/cost/budgets", params={
        "project_id": "proj-budget-2", "page": 1, "size": 10,
    })
    assert resp.json()["data"]["total"] == 1
    assert resp.json()["data"]["records"][0]["budgetId"] == "bud-list-1"

    resp = await client.get("/api/cost/budgets", params={
        "status": "APPROVED", "page": 1, "size": 10,
    })
    assert resp.json()["data"]["total"] == 1


@pytest.mark.asyncio
async def test_update_budget(client, db_session):
    """Update an existing budget."""
    db_session.add(Budget(
        budget_id="bud-update-1",
        project_id="proj-budget-4",
        budget_year=2026,
        total_budget=Decimal("100000.00"),
        status="DRAFT",
    ))
    await db_session.flush()

    resp = await client.put("/api/cost/budgets/bud-update-1", json={
        "total_budget": 150000.0,
        "status": "APPROVED",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_update_budget_not_found(client, db_session):
    """Update a non-existent budget raises 404."""
    resp = await client.put("/api/cost/budgets/nonexistent-id", json={
        "total_budget": 999.0,
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_approve_budget(client, db_session):
    """Approve a draft budget."""
    db_session.add(Budget(
        budget_id="bud-approve-1",
        project_id="proj-budget-5",
        budget_year=2026,
        total_budget=Decimal("50000.00"),
        status="DRAFT",
    ))
    await db_session.flush()

    resp = await client.post("/api/cost/budgets/bud-approve-1/approve")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_approve_budget_not_found(client, db_session):
    """Approve a non-existent budget raises 404."""
    resp = await client.post("/api/cost/budgets/nonexistent-id/approve")
    assert resp.status_code == 404


# ── Cost List + Create ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_cost(client, db_session):
    """Create a new cost record."""
    resp = await client.post("/api/cost/costs", json={
        "project_id": "proj-cost-1",
        "cost_type": "LABOR",
        "amount": 5000.0,
        "evm_pv": 10000.0,
        "evm_ev": 8000.0,
        "evm_ac": 5000.0,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SUCCESS"
    assert "costId" in body["data"]


@pytest.mark.asyncio
async def test_list_costs_with_data(client, db_session):
    """List costs with filtering by project_id and cost_type."""
    db_session.add(Cost(
        cost_id="cost-list-1",
        project_id="proj-cost-2",
        cost_type="LABOR",
        amount=Decimal("10000.00"),
        evm_pv=Decimal("15000.00"),
        evm_ev=Decimal("12000.00"),
        evm_ac=Decimal("10000.00"),
    ))
    db_session.add(Cost(
        cost_id="cost-list-2",
        project_id="proj-cost-2",
        cost_type="OUTSOURCE",
        amount=Decimal("20000.00"),
    ))
    await db_session.flush()

    resp = await client.get("/api/cost/costs", params={
        "project_id": "proj-cost-2", "page": 1, "size": 10,
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 2

    resp = await client.get("/api/cost/costs", params={
        "cost_type": "LABOR", "page": 1, "size": 10,
    })
    assert resp.json()["data"]["total"] == 1
    assert resp.json()["data"]["records"][0]["costType"] == "LABOR"


# ── EVM Calculation ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_calculate_evm(client, db_session):
    """Calculate EVM metrics for a project with EVM data."""
    db_session.add(Project(
        project_id="proj-evm-1",
        project_name="EVM Project",
        project_code="EVM-001",
        status="active",
        budget=Decimal("500000.00"),
        evm_pv=Decimal("100000.00"),
        evm_ev=Decimal("80000.00"),
        evm_ac=Decimal("90000.00"),
    ))
    await db_session.flush()

    resp = await client.post("/api/cost/projects/proj-evm-1/evm")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SUCCESS"
    data = body["data"]
    assert data["projectId"] == "proj-evm-1"
    assert data["pv"] == 100000.0
    assert data["ev"] == 80000.0
    assert data["ac"] == 90000.0
    assert data["bac"] == 500000.0
    # CPI = EV / AC = 80000 / 90000 = ~0.889
    assert abs(data["cpi"] - 80000.0 / 90000.0) < 0.01
    # SPI = EV / PV = 80000 / 100000 = 0.8
    assert abs(data["spi"] - 0.8) < 0.01


@pytest.mark.asyncio
async def test_calculate_evm_project_not_found(client, db_session):
    """Calculate EVM for non-existent project raises 404."""
    resp = await client.post("/api/cost/projects/nonexistent-project/evm")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_calculate_evm_zero_division(client, db_session):
    """Calculate EVM handles zero PV and AC gracefully."""
    db_session.add(Project(
        project_id="proj-evm-zero",
        project_name="Zero EVM Project",
        project_code="EVM-ZERO",
        status="active",
        budget=Decimal("100000.00"),
    ))
    await db_session.flush()

    resp = await client.post("/api/cost/projects/proj-evm-zero/evm")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["cpi"] == 0.0
    assert data["spi"] == 0.0
    assert data["eac"] == 100000.0


# ── Cost Alert CRUD + Ack ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_alert(client, db_session):
    """Create a new cost alert."""
    resp = await client.post("/api/cost/alerts", json={
        "project_id": "proj-alert-1",
        "budget_id": "bud-alert-1",
        "alert_type": "OVER_BUDGET",
        "threshold": 90.0,
        "current_value": 95.0,
        "message": "Budget exceeded 90% threshold",
        "severity": "HIGH",
        "status": "ACTIVE",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SUCCESS"
    assert "alertId" in body["data"]


@pytest.mark.asyncio
async def test_list_alerts(client, db_session):
    """List alerts with filtering."""
    db_session.add(CostAlert(
        alert_id="alert-list-1",
        project_id="proj-alert-2",
        budget_id="bud-alert-2",
        alert_type="OVER_BUDGET",
        threshold=Decimal("80.00"),
        current_value=Decimal("85.00"),
        message="Warning",
        severity="MEDIUM",
        status="ACTIVE",
    ))
    await db_session.flush()

    resp = await client.get("/api/cost/alerts")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) >= 1

    resp = await client.get("/api/cost/alerts", params={"project_id": "proj-alert-2"})
    assert len(resp.json()["data"]) >= 1
    assert resp.json()["data"][0]["projectId"] == "proj-alert-2"


@pytest.mark.asyncio
async def test_ack_alert(client, db_session):
    """Acknowledge an active alert."""
    db_session.add(CostAlert(
        alert_id="alert-ack-1",
        project_id="proj-alert-3",
        alert_type="OVER_BUDGET",
        status="ACTIVE",
        is_handled=0,
    ))
    await db_session.flush()

    resp = await client.put("/api/cost/alerts/alert-ack-1/ack")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_ack_alert_not_found(client, db_session):
    """Acknowledge a non-existent alert raises 404."""
    resp = await client.put("/api/cost/alerts/nonexistent-alert/ack")
    assert resp.status_code == 404


# ── Expense CRUD + Approve/Reject ──────────────────────────────────

@pytest.mark.asyncio
async def test_create_expense(client, db_session):
    """Create a new expense reimbursement."""
    resp = await client.post("/api/cost/expenses", json={
        "user_id": "user-exp-1",
        "project_id": "proj-exp-1",
        "expense_type": "TRAVEL",
        "amount": 1500.0,
        "description": "Client visit travel expense",
        "status": "pending",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SUCCESS"
    assert "expenseId" in body["data"]


@pytest.mark.asyncio
async def test_list_expenses(client, db_session):
    """List expenses with filtering by user_id and status."""
    db_session.add(ExpenseReimbursement(
        expense_id="exp-list-1",
        user_id="user-exp-2",
        project_id="proj-exp-2",
        expense_type="MEAL",
        amount=Decimal("200.00"),
        description="Team lunch",
        status="pending",
    ))
    db_session.add(ExpenseReimbursement(
        expense_id="exp-list-2",
        user_id="user-exp-3",
        expense_type="TRAVEL",
        amount=Decimal("800.00"),
        status="approved",
    ))
    await db_session.flush()

    resp = await client.get("/api/cost/expenses", params={
        "user_id": "user-exp-2", "page": 1, "size": 10,
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 1

    resp = await client.get("/api/cost/expenses", params={
        "status": "approved", "page": 1, "size": 10,
    })
    assert resp.json()["data"]["total"] == 1


@pytest.mark.asyncio
async def test_approve_expense(client, db_session):
    """Approve a pending expense."""
    db_session.add(ExpenseReimbursement(
        expense_id="exp-approve-1",
        user_id="user-exp-4",
        expense_type="TRAVEL",
        amount=Decimal("500.00"),
        status="pending",
    ))
    await db_session.flush()

    resp = await client.post("/api/cost/expenses/exp-approve-1/approve")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_approve_expense_not_found(client, db_session):
    """Approve a non-existent expense raises 404."""
    resp = await client.post("/api/cost/expenses/nonexistent-exp/approve")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_reject_expense(client, db_session):
    """Reject a pending expense."""
    db_session.add(ExpenseReimbursement(
        expense_id="exp-reject-1",
        user_id="user-exp-5",
        expense_type="MEAL",
        amount=Decimal("300.00"),
        status="pending",
    ))
    await db_session.flush()

    resp = await client.post("/api/cost/expenses/exp-reject-1/reject")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_reject_expense_not_found(client, db_session):
    """Reject a non-existent expense raises 404."""
    resp = await client.post("/api/cost/expenses/nonexistent-exp/reject")
    assert resp.status_code == 404


# ── Settlement CRUD + Approve/Reject ───────────────────────────────

@pytest.mark.asyncio
async def test_create_settlement(client, db_session):
    """Create a new cost settlement."""
    db_session.add(Project(
        project_id="proj-settle-1",
        project_name="Settlement Project",
        project_code="SETTLE-001",
        status="active",
    ))
    await db_session.flush()

    resp = await client.post("/api/cost/settlements", json={
        "project_id": "proj-settle-1",
        "settlement_amount": 250000.0,
        "status": "pending",
        "created_by": "admin",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SUCCESS"
    assert "settlementId" in body["data"]


@pytest.mark.asyncio
async def test_list_settlements(client, db_session):
    """List settlements with filtering."""
    db_session.add(CostSettlement(
        settlement_id="set-list-1",
        project_id="proj-settle-2",
        settlement_amount=Decimal("100000.00"),
        status="pending",
    ))
    await db_session.flush()

    resp = await client.get("/api/cost/settlements", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] >= 1

    resp = await client.get("/api/cost/settlements", params={
        "project_id": "proj-settle-2", "page": 1, "size": 10,
    })
    assert resp.json()["data"]["total"] >= 1


@pytest.mark.asyncio
async def test_approve_settlement(client, db_session):
    """Approve a pending settlement."""
    db_session.add(CostSettlement(
        settlement_id="set-approve-1",
        project_id="proj-settle-3",
        settlement_amount=Decimal("150000.00"),
        status="pending",
    ))
    await db_session.flush()

    resp = await client.post("/api/cost/settlements/set-approve-1/approve")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_reject_settlement(client, db_session):
    """Reject a settlement with reason."""
    db_session.add(CostSettlement(
        settlement_id="set-reject-1",
        project_id="proj-settle-4",
        settlement_amount=Decimal("80000.00"),
        status="pending",
    ))
    await db_session.flush()

    resp = await client.post("/api/cost/settlements/set-reject-1/reject", json={
        "reason": "Amount does not match contract",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_approve_settlement_not_found(client, db_session):
    """Approve a non-existent settlement raises 404."""
    resp = await client.post("/api/cost/settlements/nonexistent-settle/approve")
    assert resp.status_code == 404


# ── Cost Trend ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cost_trend(client, db_session):
    """Get cost trend for a project with cost records."""
    db_session.add(Project(
        project_id="proj-trend-1",
        project_name="Trend Project",
        project_code="TREND-001",
        status="active",
        budget=Decimal("200000.00"),
    ))
    db_session.add(Cost(
        cost_id="cost-trend-1",
        project_id="proj-trend-1",
        cost_type="LABOR",
        amount=Decimal("5000.00"),
        calculate_time=datetime(2026, 1, 15, tzinfo=timezone.utc),
    ))
    db_session.add(Cost(
        cost_id="cost-trend-2",
        project_id="proj-trend-1",
        cost_type="OUTSOURCE",
        amount=Decimal("10000.00"),
        calculate_time=datetime(2026, 2, 15, tzinfo=timezone.utc),
    ))
    # EVM_SNAPSHOT entries should be excluded from trend
    db_session.add(Cost(
        cost_id="cost-trend-snapshot",
        project_id="proj-trend-1",
        cost_type="EVM_SNAPSHOT",
        amount=Decimal("15000.00"),
        calculate_time=datetime(2026, 3, 1, tzinfo=timezone.utc),
    ))
    await db_session.flush()

    resp = await client.get("/api/cost/trend/proj-trend-1")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SUCCESS"
    assert body["data"]["projectId"] == "proj-trend-1"
    # Only non-EVM_SNAPSHOT costs should appear
    assert len(body["data"]["trend"]) == 2
    assert body["data"]["trend"][0]["type"] == "LABOR"
    assert body["data"]["trend"][1]["type"] == "OUTSOURCE"


@pytest.mark.asyncio
async def test_cost_trend_empty(client, db_session):
    """Get cost trend for a project with no cost records."""
    db_session.add(Project(
        project_id="proj-trend-empty",
        project_name="Empty Trend Project",
        project_code="TREND-EMPTY",
        status="active",
    ))
    await db_session.flush()

    resp = await client.get("/api/cost/trend/proj-trend-empty")
    assert resp.status_code == 200
    assert resp.json()["data"]["trend"] == []


# ── Budget Execution Rate ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_budget_execution_rate(client, db_session):
    """Calculate budget execution rate with costs."""
    db_session.add(Project(
        project_id="proj-exec-1",
        project_name="Execution Rate Project",
        project_code="EXEC-001",
        status="active",
        budget=Decimal("500000.00"),
    ))
    db_session.add(Budget(
        budget_id="bud-exec-1",
        project_id="proj-exec-1",
        budget_year=2026,
        total_budget=Decimal("500000.00"),
        status="APPROVED",
    ))
    db_session.add(Cost(
        cost_id="cost-exec-1",
        project_id="proj-exec-1",
        cost_type="LABOR",
        amount=Decimal("150000.00"),
    ))
    await db_session.flush()

    resp = await client.get("/api/cost/budget-execution", params={
        "project_id": "proj-exec-1",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "SUCCESS"
    data = body["data"]
    assert len(data) >= 1
    exec_item = next(d for d in data if d["budgetId"] == "bud-exec-1")
    assert exec_item["budget"] == 500000.0
    assert exec_item["actual"] == 150000.0
    # Execution rate = 150000 / 500000 * 100 = 30.0
    assert exec_item["executionRate"] == 30.0


@pytest.mark.asyncio
async def test_budget_execution_rate_no_costs(client, db_session):
    """Calculate budget execution rate with zero actual spend."""
    db_session.add(Budget(
        budget_id="bud-exec-zero",
        project_id="proj-exec-zero",
        budget_year=2026,
        total_budget=Decimal("100000.00"),
        status="DRAFT",
    ))
    await db_session.flush()

    resp = await client.get("/api/cost/budget-execution", params={
        "project_id": "proj-exec-zero",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) >= 1
    exec_item = next(d for d in data if d["budgetId"] == "bud-exec-zero")
    assert exec_item["actual"] == 0.0
    assert exec_item["executionRate"] == 0.0
