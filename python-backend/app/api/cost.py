"""Cost API router — consolidates 5 cost controllers."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ApiResponse, PageResult
from app.database import get_db
from app.exceptions import BusinessError, ResourceNotFoundError
from app.models.cost.models import Budget, Cost, CostAlert, CostOutsource, ExpenseReimbursement

router = APIRouter(tags=["cost"])


# ── Budgets ──────────────────────────────────────────────────────────

@router.get("/budgets")
async def list_budgets(
    project_id: str | None = None, status: str | None = None,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Budget).order_by(Budget.create_time.desc())
    if project_id:
        stmt = stmt.where(Budget.project_id == project_id)
    if status:
        stmt = stmt.where(Budget.status == status)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[_budget_to_dict(b) for b in items],
    ))


@router.post("/budgets")
async def create_budget(req: BudgetCreateRequest, db: AsyncSession = Depends(get_db)):
    budget = Budget(
        budget_id=str(uuid.uuid4()), project_id=req.project_id,
        budget_year=req.budget_year, total_budget=req.total_budget,
        labor_budget=req.labor_budget, outsource_budget=req.outsource_budget,
        procurement_budget=req.procurement_budget, other_budget=req.other_budget,
        status=req.status or "DRAFT",
    )
    db.add(budget)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"budgetId": budget.budget_id})


@router.put("/budgets/{budget_id}")
async def update_budget(budget_id: str, req: BudgetUpdateRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Budget).where(Budget.budget_id == budget_id)
    budget = (await db.execute(stmt)).scalar_one_or_none()
    if not budget:
        raise ResourceNotFoundError("预算", budget_id)
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(budget, field, value)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.post("/budgets/{budget_id}/approve")
async def approve_budget(budget_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Budget).where(Budget.budget_id == budget_id)
    budget = (await db.execute(stmt)).scalar_one_or_none()
    if not budget:
        raise ResourceNotFoundError("预算", budget_id)
    budget.status = "APPROVED"
    budget.approved_date = datetime.now(timezone.utc)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="审批通过")


# ── Costs ────────────────────────────────────────────────────────────

@router.get("/costs")
async def list_costs(
    project_id: str | None = None, cost_type: str | None = None,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Cost).order_by(Cost.create_time.desc())
    if project_id:
        stmt = stmt.where(Cost.project_id == project_id)
    if cost_type:
        stmt = stmt.where(Cost.cost_type == cost_type)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{"costId": c.cost_id, "projectId": c.project_id, "costType": c.cost_type,
                 "amount": float(c.amount), "evmPv": float(c.evm_pv) if c.evm_pv else None,
                 "evmEv": float(c.evm_ev) if c.evm_ev else None,
                 "evmAc": float(c.evm_ac) if c.evm_ac else None} for c in items],
    ))


@router.post("/costs")
async def create_cost(req: CostCreateRequest, db: AsyncSession = Depends(get_db)):
    cost = Cost(
        cost_id=str(uuid.uuid4()), project_id=req.project_id,
        cost_type=req.cost_type, amount=req.amount,
        calculate_time=req.calculate_time,
        evm_pv=req.evm_pv, evm_ev=req.evm_ev, evm_ac=req.evm_ac,
    )
    db.add(cost)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"costId": cost.cost_id})


# ── EVM Calculation ──────────────────────────────────────────────────

@router.post("/projects/{project_id}/evm")
async def calculate_evm(project_id: str, db: AsyncSession = Depends(get_db)):
    from app.models.project.models import Project

    project_stmt = select(Project).where(Project.project_id == project_id)
    project = (await db.execute(project_stmt)).scalar_one_or_none()
    if not project:
        raise ResourceNotFoundError("项目", project_id)

    pv = project.evm_pv or Decimal("0")
    ac = project.evm_ac or Decimal("0")
    ev = project.evm_ev or Decimal("0")
    bac = project.budget or Decimal("0")

    cpi = ev / ac if ac > 0 else Decimal("0")
    spi = ev / pv if pv > 0 else Decimal("0")
    eac = bac / cpi if cpi > 0 else bac

    # Save as EVM_SNAPSHOT cost record
    snapshot = Cost(
        cost_id=str(uuid.uuid4()), project_id=project_id,
        cost_type="EVM_SNAPSHOT", amount=ac,
        evm_pv=pv, evm_ev=ev, evm_ac=ac,
        calculate_time=datetime.now(timezone.utc),
    )
    db.add(snapshot)

    # Update project EVM metrics
    project.evm_cpi = cpi
    project.evm_spi = spi

    await db.flush()

    return ApiResponse(code="SUCCESS", message="success", data={
        "projectId": project_id,
        "pv": float(pv), "ac": float(ac), "ev": float(ev),
        "cpi": float(cpi), "spi": float(spi),
        "eac": float(eac), "bac": float(bac),
    })


# ── Cost Alerts ──────────────────────────────────────────────────────

@router.get("/alerts")
async def list_alerts(
    project_id: str | None = None, status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(CostAlert).order_by(CostAlert.create_time.desc())
    if project_id:
        stmt = stmt.where(CostAlert.project_id == project_id)
    if status:
        stmt = stmt.where(CostAlert.status == status)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"alertId": a.alert_id, "projectId": a.project_id, "budgetId": a.budget_id,
         "alertType": a.alert_type, "threshold": float(a.threshold) if a.threshold else None,
         "currentValue": float(a.current_value) if a.current_value else None,
         "message": a.message, "isHandled": a.is_handled, "severity": a.severity,
         "status": a.status} for a in items
    ])


@router.post("/alerts")
async def create_alert(req: AlertCreateRequest, db: AsyncSession = Depends(get_db)):
    alert = CostAlert(
        alert_id=str(uuid.uuid4()), project_id=req.project_id,
        budget_id=req.budget_id, alert_type=req.alert_type,
        threshold=req.threshold, current_value=req.current_value,
        message=req.message, severity=req.severity, status=req.status or "ACTIVE",
    )
    db.add(alert)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"alertId": alert.alert_id})


@router.put("/alerts/{alert_id}/ack")
async def ack_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(CostAlert).where(CostAlert.alert_id == alert_id)
    alert = (await db.execute(stmt)).scalar_one_or_none()
    if not alert:
        raise ResourceNotFoundError("告警", alert_id)
    alert.is_handled = 1
    alert.ack_time = datetime.now(timezone.utc)
    alert.status = "ACKNOWLEDGED"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Expenses ─────────────────────────────────────────────────────────

@router.get("/expenses")
async def list_expenses(
    user_id: str | None = None, status: str | None = None,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ExpenseReimbursement).order_by(ExpenseReimbursement.create_time.desc())
    if user_id:
        stmt = stmt.where(ExpenseReimbursement.user_id == user_id)
    if status:
        stmt = stmt.where(ExpenseReimbursement.status == status)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{"expenseId": e.expense_id, "userId": e.user_id, "projectId": e.project_id,
                 "expenseType": e.expense_type, "amount": float(e.amount),
                 "applyDate": str(e.apply_date) if e.apply_date else None,
                 "description": e.description, "status": e.status,
                 "approverId": e.approver_id} for e in items],
    ))


@router.post("/expenses")
async def create_expense(req: ExpenseCreateRequest, db: AsyncSession = Depends(get_db)):
    expense = ExpenseReimbursement(
        expense_id=str(uuid.uuid4()), user_id=req.user_id,
        project_id=req.project_id, expense_type=req.expense_type,
        amount=req.amount, apply_date=req.apply_date,
        description=req.description, attachments=req.attachments,
        status=req.status or "pending",
    )
    db.add(expense)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"expenseId": expense.expense_id})


@router.post("/expenses/{expense_id}/approve")
async def approve_expense(expense_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ExpenseReimbursement).where(ExpenseReimbursement.expense_id == expense_id)
    expense = (await db.execute(stmt)).scalar_one_or_none()
    if not expense:
        raise ResourceNotFoundError("报销", expense_id)
    expense.status = "approved"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="审批通过")


@router.post("/expenses/{expense_id}/reject")
async def reject_expense(expense_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ExpenseReimbursement).where(ExpenseReimbursement.expense_id == expense_id)
    expense = (await db.execute(stmt)).scalar_one_or_none()
    if not expense:
        raise ResourceNotFoundError("报销", expense_id)
    expense.status = "rejected"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="已拒绝")


# ── Cost Analysis ────────────────────────────────────────────────────

@router.get("/analysis/{project_id}")
async def cost_analysis(project_id: str, db: AsyncSession = Depends(get_db)):
    from app.models.project.models import Project

    project_stmt = select(Project).where(Project.project_id == project_id)
    project = (await db.execute(project_stmt)).scalar_one_or_none()
    if not project:
        raise ResourceNotFoundError("项目", project_id)

    cost_stmt = select(
        Cost.cost_type,
        func.sum(Cost.amount).label("total"),
    ).where(Cost.project_id == project_id).group_by(Cost.cost_type)
    cost_result = await db.execute(cost_stmt)
    breakdown = {row[0]: float(row[1]) for row in cost_result}

    budget_stmt = select(Budget).where(Budget.project_id == project_id)
    budget = (await db.execute(budget_stmt)).scalar_one_or_none()

    total_cost = sum(breakdown.values())
    total_budget = float(project.budget) if project.budget else 0

    return ApiResponse(code="SUCCESS", message="success", data={
        "projectId": project_id,
        "totalCost": total_cost,
        "totalBudget": total_budget,
        "variance": total_budget - total_cost,
        "variancePercent": ((total_budget - total_cost) / total_budget * 100) if total_budget > 0 else 0,
        "breakdown": breakdown,
        "budget": _budget_to_dict(budget) if budget else None,
    })


# ── Cost Settlement ──────────────────────────────────────────────────

@router.post("/settlements")
async def create_settlement(
    req: CostSettlementRequest, db: AsyncSession = Depends(get_db),
):
    """Create cost settlement record."""
    from app.models.cost.models import CostSettlement
    settlement = CostSettlement(
        settlement_id=str(uuid.uuid4()),
        project_id=req.project_id,
        settlement_amount=req.settlement_amount,
        settlement_date=req.settlement_date or datetime.now(timezone.utc),
        status=req.status or "pending",
        created_by=req.created_by,
    )
    db.add(settlement)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"settlementId": settlement.settlement_id})


@router.get("/settlements")
async def list_settlements(
    project_id: str | None = None, status: str | None = None,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List cost settlements."""
    from app.models.cost.models import CostSettlement
    stmt = select(CostSettlement).order_by(CostSettlement.settlement_date.desc())
    if project_id:
        stmt = stmt.where(CostSettlement.project_id == project_id)
    if status:
        stmt = stmt.where(CostSettlement.status == status)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{
            "settlementId": s.settlement_id, "projectId": s.project_id,
            "settlementAmount": float(s.settlement_amount) if s.settlement_amount else None,
            "settlementDate": str(s.settlement_date) if s.settlement_date else None,
            "status": s.status,
        } for s in items],
    ))


@router.post("/settlements/{settlement_id}/approve")
async def approve_settlement(settlement_id: str, db: AsyncSession = Depends(get_db)):
    """Approve cost settlement."""
    from app.models.cost.models import CostSettlement
    s = await db.get(CostSettlement, settlement_id)
    if not s:
        raise ResourceNotFoundError("结算", settlement_id)
    s.status = "approved"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.post("/settlements/{settlement_id}/reject")
async def reject_settlement(
    settlement_id: str, req: SettlementRejectRequest, db: AsyncSession = Depends(get_db),
):
    """Reject cost settlement."""
    from app.models.cost.models import CostSettlement
    s = await db.get(CostSettlement, settlement_id)
    if not s:
        raise ResourceNotFoundError("结算", settlement_id)
    s.status = "rejected"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Cost Trend ───────────────────────────────────────────────────────

@router.get("/trend/{project_id}")
async def cost_trend(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get cost trend over time for a project."""
    stmt = select(Cost).where(
        Cost.project_id == project_id,
        Cost.cost_type != "EVM_SNAPSHOT",
    ).order_by(Cost.calculate_time.asc())
    result = await db.execute(stmt)
    items = result.scalars().all()
    trend = [
        {
            "date": str(c.calculate_time) if c.calculate_time else None,
            "amount": float(c.amount),
            "type": c.cost_type,
        }
        for c in items
    ]
    return ApiResponse(code="SUCCESS", message="success", data={"projectId": project_id, "trend": trend})


# ── Budget Execution Rate ────────────────────────────────────────────

@router.get("/budget-execution")
async def budget_execution_rate(
    project_id: str | None = None, db: AsyncSession = Depends(get_db),
):
    """Get budget execution rate (actual spend / budget)."""
    budgets_stmt = select(Budget)
    if project_id:
        budgets_stmt = budgets_stmt.where(Budget.project_id == project_id)
    budgets_result = await db.execute(budgets_stmt)
    budgets = budgets_result.scalars().all()

    result_data = []
    for b in budgets:
        cost_stmt = select(func.sum(Cost.amount)).where(Cost.project_id == b.project_id)
        actual = (await db.execute(cost_stmt)).scalar() or Decimal("0")
        total_budget = b.total_budget or Decimal("0")
        rate = float(actual / total_budget * 100) if total_budget > 0 else 0
        result_data.append({
            "budgetId": b.budget_id,
            "projectId": b.project_id,
            "budget": float(total_budget),
            "actual": float(actual),
            "executionRate": round(rate, 2),
        })
    return ApiResponse(code="SUCCESS", message="success", data=result_data)


# ── Cost Outsourcing ─────────────────────────────────────────────────

@router.get("/outsource")
async def list_outsource(project_id: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(CostOutsource)
    if project_id:
        stmt = stmt.where(CostOutsource.project_id == project_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"outsourceId": o.outsource_id, "projectId": o.project_id, "vendorName": o.vendor_name,
         "contractAmount": float(o.contract_amount) if o.contract_amount else None,
         "paidAmount": float(o.paid_amount) if o.paid_amount else None, "status": o.status} for o in items
    ])


# ── Legacy aliases (frontend compatibility) ──────────────────────────

@router.get("/budgets/list")
async def list_budgets_alias(
    project_id: str | None = None, status: str | None = None,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await list_budgets(project_id=project_id, status=status, page=page, size=size, db=db)


@router.get("/budget/list")
async def list_budgets_singular(
    project_id: str | None = None, status: str | None = None,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await list_budgets(project_id=project_id, status=status, page=page, size=size, db=db)


@router.get("/evm/{project_id}")
async def get_evm(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get EVM data for a project."""
    stmt = select(Cost).where(Cost.project_id == project_id).order_by(Cost.calculate_time.desc()).limit(1)
    result = await db.execute(stmt)
    cost = result.scalar_one_or_none()
    if cost:
        cpi = float(cost.evm_ev / cost.evm_ac) if cost.evm_ac and cost.evm_ac > 0 else None
        spi = float(cost.evm_ev / cost.evm_pv) if cost.evm_pv and cost.evm_pv > 0 else None
    else:
        cpi = spi = None
    return ApiResponse(code="SUCCESS", message="success", data={
        "projectId": project_id, "cpi": cpi, "spi": spi,
        "evmPv": float(cost.evm_pv) if cost and cost.evm_pv else None,
        "evmEv": float(cost.evm_ev) if cost and cost.evm_ev else None,
        "evmAc": float(cost.evm_ac) if cost and cost.evm_ac else None,
    })


@router.get("/dashboard")
async def cost_dashboard(db: AsyncSession = Depends(get_db)):
    """Cost dashboard summary."""
    total_budget = (await db.execute(select(func.sum(Budget.total_budget)))).scalar() or 0
    total_cost = (await db.execute(select(func.sum(Cost.amount)))).scalar() or 0
    return ApiResponse(code="SUCCESS", message="success", data={
        "totalBudget": float(total_budget), "totalCost": float(total_cost),
        "remaining": float(total_budget) - float(total_cost),
    })


# ── Helpers ──────────────────────────────────────────────────────────

def _budget_to_dict(b: Budget) -> dict:
    return {
        "budgetId": b.budget_id, "projectId": b.project_id,
        "budgetYear": b.budget_year, "totalBudget": float(b.total_budget) if b.total_budget else None,
        "laborBudget": float(b.labor_budget) if b.labor_budget else None,
        "outsourceBudget": float(b.outsource_budget) if b.outsource_budget else None,
        "procurementBudget": float(b.procurement_budget) if b.procurement_budget else None,
        "otherBudget": float(b.other_budget) if b.other_budget else None,
        "status": b.status, "approvedBy": b.approved_by,
        "approvedDate": str(b.approved_date) if b.approved_date else None,
    }


# ── Request schemas ──────────────────────────────────────────────────

class BudgetCreateRequest(BaseModel):
    project_id: str
    budget_year: int | None = None
    total_budget: float | None = None
    labor_budget: float | None = None
    outsource_budget: float | None = None
    procurement_budget: float | None = None
    other_budget: float | None = None
    status: str | None = None

class BudgetUpdateRequest(BaseModel):
    total_budget: float | None = None
    labor_budget: float | None = None
    outsource_budget: float | None = None
    procurement_budget: float | None = None
    other_budget: float | None = None
    status: str | None = None

class CostCreateRequest(BaseModel):
    project_id: str
    cost_type: str
    amount: float
    calculate_time: datetime | None = None
    evm_pv: float | None = None
    evm_ev: float | None = None
    evm_ac: float | None = None

class AlertCreateRequest(BaseModel):
    project_id: str
    budget_id: str | None = None
    alert_type: str | None = None
    threshold: float | None = None
    current_value: float | None = None
    message: str | None = None
    severity: str | None = None
    status: str | None = None

class ExpenseCreateRequest(BaseModel):
    user_id: str
    project_id: str | None = None
    expense_type: str | None = None
    amount: float
    apply_date: datetime | None = None
    description: str | None = None
    attachments: str | None = None
    status: str | None = None


class CostSettlementRequest(BaseModel):
    project_id: str
    settlement_amount: float
    settlement_date: datetime | None = None
    status: str | None = None
    created_by: str | None = None


class SettlementRejectRequest(BaseModel):
    reason: str | None = None
