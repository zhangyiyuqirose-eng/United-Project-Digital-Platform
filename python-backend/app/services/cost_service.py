"""Cost domain service — budgets, costs, alerts, outsource, expenses, settlements."""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import PageResult
from app.exceptions import BusinessError, ResourceNotFoundError
from app.models.cost.models import (
    Budget,
    Cost,
    CostAlert,
    CostOutsource,
    CostSettlement,
    ExpenseReimbursement,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _compute_cpi_spi_eac(pv: Decimal, ev: Decimal, ac: Decimal) -> dict[str, float]:
    """Return CPI, SPI, and EAC from PV/EV/AC values."""
    pv_f = float(pv or 0)
    ev_f = float(ev or 0)
    ac_f = float(ac or 0)
    cpi = (ev_f / ac_f) if ac_f > 0 else 1.0
    spi = (ev_f / pv_f) if pv_f > 0 else 1.0
    eac = (ac_f / cpi) if cpi > 0 else ac_f
    return {"pv": pv_f, "ev": ev_f, "ac": ac_f, "cpi": round(cpi, 4), "spi": round(spi, 4), "eac": round(eac, 2)}


class CostService:
    """Encapsulates all cost-domain database operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Budget ─────────────────────────────────────────────────────────

    async def list_budgets(
        self, project_id: str | None = None, page: int = 1, size: int = 20
    ) -> PageResult:
        base = select(Budget)
        if project_id:
            base = base.where(Budget.project_id == project_id)
        base = base.order_by(Budget.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_budget_dict(b) for b in result.scalars().all()],
        )

    async def get_budget(self, budget_id: str) -> dict[str, object]:
        b = await self._get_budget_or_404(budget_id)
        return _budget_dict(b)

    async def create_budget(self, **kwargs: object) -> dict[str, str]:
        budget = Budget(budget_id=str(uuid.uuid4()), **kwargs)
        self.db.add(budget)
        await self.db.flush()
        return {"budgetId": budget.budget_id}

    async def update_budget(self, budget_id: str, **kwargs: object) -> None:
        b = await self._get_budget_or_404(budget_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(b, k):
                setattr(b, k, v)
        await self.db.flush()

    async def delete_budget(self, budget_id: str) -> None:
        b = await self._get_budget_or_404(budget_id)
        await self.db.delete(b)
        await self.db.flush()

    async def approve_budget(self, budget_id: str, approver_id: str) -> dict[str, str]:
        b = await self._get_budget_or_404(budget_id)
        b.status = "APPROVED"
        b.approved_by = approver_id
        b.approved_date = _now()
        await self.db.flush()
        return {"budgetId": budget_id, "status": b.status}

    # ── Cost ────────────────────────────────────────────────────────────

    async def list_costs(
        self, project_id: str | None = None, page: int = 1, size: int = 20
    ) -> PageResult:
        base = select(Cost)
        if project_id:
            base = base.where(Cost.project_id == project_id)
        base = base.order_by(Cost.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_cost_dict(c) for c in result.scalars().all()],
        )

    async def get_cost(self, cost_id: str) -> dict[str, object]:
        c = await self._get_cost_or_404(cost_id)
        return _cost_dict(c)

    async def create_cost(self, **kwargs: object) -> dict[str, str]:
        cost = Cost(cost_id=str(uuid.uuid4()), **kwargs)
        self.db.add(cost)
        await self.db.flush()
        return {"costId": cost.cost_id}

    async def update_cost(self, cost_id: str, **kwargs: object) -> None:
        c = await self._get_cost_or_404(cost_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(c, k):
                setattr(c, k, v)
        await self.db.flush()

    async def delete_cost(self, cost_id: str) -> None:
        c = await self._get_cost_or_404(cost_id)
        await self.db.delete(c)
        await self.db.flush()

    async def calculate_evm(self, project_id: str) -> dict[str, float]:
        """Aggregate PV/EV/AC across all cost records for a project and compute CPI/SPI/EAC."""
        stmt = select(
            func.sum(Cost.evm_pv).label("total_pv"),
            func.sum(Cost.evm_ev).label("total_ev"),
            func.sum(Cost.evm_ac).label("total_ac"),
        ).where(Cost.project_id == project_id)
        result = await self.db.execute(stmt)
        row = result.first()
        pv = row[0] or Decimal("0")
        ev = row[1] or Decimal("0")
        ac = row[2] or Decimal("0")
        return _compute_cpi_spi_eac(pv, ev, ac)

    # ── Cost Alert ──────────────────────────────────────────────────────

    async def list_alerts(
        self, project_id: str | None = None, page: int = 1, size: int = 20
    ) -> PageResult:
        base = select(CostAlert)
        if project_id:
            base = base.where(CostAlert.project_id == project_id)
        base = base.order_by(CostAlert.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_alert_dict(a) for a in result.scalars().all()],
        )

    async def get_alert(self, alert_id: str) -> dict[str, object]:
        a = await self._get_alert_or_404(alert_id)
        return _alert_dict(a)

    async def create_alert(self, **kwargs: object) -> dict[str, str]:
        alert = CostAlert(alert_id=str(uuid.uuid4()), **kwargs)
        self.db.add(alert)
        await self.db.flush()
        return {"alertId": alert.alert_id}

    async def update_alert(self, alert_id: str, **kwargs: object) -> None:
        a = await self._get_alert_or_404(alert_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(a, k):
                setattr(a, k, v)
        await self.db.flush()

    async def delete_alert(self, alert_id: str) -> None:
        a = await self._get_alert_or_404(alert_id)
        await self.db.delete(a)
        await self.db.flush()

    async def ack_alert(self, alert_id: str) -> dict[str, str]:
        """Acknowledge a cost alert."""
        a = await self._get_alert_or_404(alert_id)
        a.is_handled = 1
        a.status = "ACKED"
        a.ack_time = _now()
        await self.db.flush()
        return {"alertId": alert_id, "status": a.status}

    # ── Expense Reimbursement ───────────────────────────────────────────

    async def list_expenses(
        self, project_id: str | None = None, user_id: str | None = None,
        page: int = 1, size: int = 20,
    ) -> PageResult:
        base = select(ExpenseReimbursement)
        if project_id:
            base = base.where(ExpenseReimbursement.project_id == project_id)
        if user_id:
            base = base.where(ExpenseReimbursement.user_id == user_id)
        base = base.order_by(ExpenseReimbursement.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_expense_dict(e) for e in result.scalars().all()],
        )

    async def get_expense(self, expense_id: str) -> dict[str, object]:
        e = await self._get_expense_or_404(expense_id)
        return _expense_dict(e)

    async def create_expense(self, **kwargs: object) -> dict[str, str]:
        exp = ExpenseReimbursement(expense_id=str(uuid.uuid4()), **kwargs)
        self.db.add(exp)
        await self.db.flush()
        return {"expenseId": exp.expense_id}

    async def update_expense(self, expense_id: str, **kwargs: object) -> None:
        e = await self._get_expense_or_404(expense_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(e, k):
                setattr(e, k, v)
        await self.db.flush()

    async def delete_expense(self, expense_id: str) -> None:
        e = await self._get_expense_or_404(expense_id)
        await self.db.delete(e)
        await self.db.flush()

    async def approve_expense(self, expense_id: str, approver_id: str) -> dict[str, str]:
        e = await self._get_expense_or_404(expense_id)
        e.status = "approved"
        e.approver_id = approver_id
        await self.db.flush()
        return {"expenseId": expense_id, "status": e.status}

    async def reject_expense(self, expense_id: str, approver_id: str) -> dict[str, str]:
        e = await self._get_expense_or_404(expense_id)
        e.status = "rejected"
        e.approver_id = approver_id
        await self.db.flush()
        return {"expenseId": expense_id, "status": e.status}

    # ── Cost trends & execution rate ────────────────────────────────────

    async def cost_trend(
        self, project_id: str, months: int = 12
    ) -> list[dict[str, object]]:
        """Monthly cost aggregation for the last N months."""
        stmt = select(Cost).where(Cost.project_id == project_id)
        result = await self.db.execute(stmt)
        costs = result.scalars().all()

        buckets: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        for c in costs:
            if c.calculate_time:
                key = c.calculate_time.strftime("%Y-%m")
                buckets[key] += c.amount or Decimal("0")

        return sorted(
            [{"month": k, "amount": float(v)} for k, v in buckets.items()],
            key=lambda x: x["month"],
        )

    async def budget_execution_rate(self, project_id: str) -> dict[str, float]:
        """Actual cost vs budget ratio for a project."""
        budget_stmt = select(func.sum(Budget.total_budget)).where(
            Budget.project_id == project_id, Budget.status == "APPROVED"
        )
        total_budget = (await self.db.execute(budget_stmt)).scalar() or Decimal("0")

        cost_stmt = select(func.sum(Cost.amount)).where(
            Cost.project_id == project_id
        )
        total_cost = (await self.db.execute(cost_stmt)).scalar() or Decimal("0")

        budget_f = float(total_budget)
        cost_f = float(total_cost)
        rate = (cost_f / budget_f * 100) if budget_f > 0 else 0.0
        return {
            "projectId": project_id,
            "totalBudget": budget_f,
            "actualCost": cost_f,
            "executionRate": round(rate, 2),
        }

    # ── Cost Outsource ──────────────────────────────────────────────────

    async def list_outsources(
        self, project_id: str | None = None, page: int = 1, size: int = 20
    ) -> PageResult:
        base = select(CostOutsource)
        if project_id:
            base = base.where(CostOutsource.project_id == project_id)
        base = base.order_by(CostOutsource.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_outsource_dict(o) for o in result.scalars().all()],
        )

    async def get_outsource(self, outsource_id: str) -> dict[str, object]:
        o = await self._get_outsource_or_404(outsource_id)
        return _outsource_dict(o)

    async def create_outsource(self, **kwargs: object) -> dict[str, str]:
        o = CostOutsource(outsource_id=str(uuid.uuid4()), **kwargs)
        self.db.add(o)
        await self.db.flush()
        return {"outsourceId": o.outsource_id}

    async def update_outsource(self, outsource_id: str, **kwargs: object) -> None:
        o = await self._get_outsource_or_404(outsource_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(o, k):
                setattr(o, k, v)
        await self.db.flush()

    async def delete_outsource(self, outsource_id: str) -> None:
        o = await self._get_outsource_or_404(outsource_id)
        await self.db.delete(o)
        await self.db.flush()

    # ── Cost Settlement ─────────────────────────────────────────────────

    async def list_settlements(
        self, project_id: str | None = None, page: int = 1, size: int = 20
    ) -> PageResult:
        base = select(CostSettlement)
        if project_id:
            base = base.where(CostSettlement.project_id == project_id)
        base = base.order_by(CostSettlement.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_settlement_dict(s) for s in result.scalars().all()],
        )

    async def get_settlement(self, settlement_id: str) -> dict[str, object]:
        s = await self._get_settlement_or_404(settlement_id)
        return _settlement_dict(s)

    async def create_settlement(self, **kwargs: object) -> dict[str, str]:
        s = CostSettlement(settlement_id=str(uuid.uuid4()), **kwargs)
        self.db.add(s)
        await self.db.flush()
        return {"settlementId": s.settlement_id}

    async def update_settlement(self, settlement_id: str, **kwargs: object) -> None:
        s = await self._get_settlement_or_404(settlement_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(s, k):
                setattr(s, k, v)
        await self.db.flush()

    # ── Internal helpers ────────────────────────────────────────────────

    async def _get_budget_or_404(self, budget_id: str) -> Budget:
        b = await self.db.get(Budget, budget_id)
        if not b:
            raise ResourceNotFoundError("预算", budget_id)
        return b

    async def _get_cost_or_404(self, cost_id: str) -> Cost:
        c = await self.db.get(Cost, cost_id)
        if not c:
            raise ResourceNotFoundError("成本记录", cost_id)
        return c

    async def _get_alert_or_404(self, alert_id: str) -> CostAlert:
        a = await self.db.get(CostAlert, alert_id)
        if not a:
            raise ResourceNotFoundError("成本告警", alert_id)
        return a

    async def _get_expense_or_404(self, expense_id: str) -> ExpenseReimbursement:
        e = await self.db.get(ExpenseReimbursement, expense_id)
        if not e:
            raise ResourceNotFoundError("报销记录", expense_id)
        return e

    async def _get_outsource_or_404(self, outsource_id: str) -> CostOutsource:
        o = await self.db.get(CostOutsource, outsource_id)
        if not o:
            raise ResourceNotFoundError("委外成本", outsource_id)
        return o

    async def _get_settlement_or_404(self, settlement_id: str) -> CostSettlement:
        s = await self.db.get(CostSettlement, settlement_id)
        if not s:
            raise ResourceNotFoundError("结算记录", settlement_id)
        return s


# ── Dict converters ──────────────────────────────────────────────────────

def _budget_dict(b: Budget) -> dict[str, object]:
    return {
        "budgetId": b.budget_id, "projectId": b.project_id,
        "budgetYear": b.budget_year,
        "totalBudget": float(b.total_budget) if b.total_budget else None,
        "laborBudget": float(b.labor_budget) if b.labor_budget else None,
        "outsourceBudget": float(b.outsource_budget) if b.outsource_budget else None,
        "procurementBudget": float(b.procurement_budget) if b.procurement_budget else None,
        "otherBudget": float(b.other_budget) if b.other_budget else None,
        "approvedBy": b.approved_by,
        "approvedDate": b.approved_date.isoformat() if b.approved_date else None,
        "status": b.status,
    }


def _cost_dict(c: Cost) -> dict[str, object]:
    return {
        "costId": c.cost_id, "projectId": c.project_id,
        "costType": c.cost_type,
        "amount": float(c.amount) if c.amount else None,
        "calculateTime": c.calculate_time.isoformat() if c.calculate_time else None,
        "evmPv": float(c.evm_pv) if c.evm_pv else None,
        "evmEv": float(c.evm_ev) if c.evm_ev else None,
        "evmAc": float(c.evm_ac) if c.evm_ac else None,
    }


def _alert_dict(a: CostAlert) -> dict[str, object]:
    return {
        "alertId": a.alert_id, "projectId": a.project_id,
        "budgetId": a.budget_id, "alertType": a.alert_type,
        "threshold": float(a.threshold) if a.threshold else None,
        "currentValue": float(a.current_value) if a.current_value else None,
        "message": a.message, "isHandled": bool(a.is_handled),
        "severity": a.severity, "status": a.status,
        "createdBy": a.created_by,
    }


def _expense_dict(e: ExpenseReimbursement) -> dict[str, object]:
    return {
        "expenseId": e.expense_id, "userId": e.user_id,
        "projectId": e.project_id, "expenseType": e.expense_type,
        "amount": float(e.amount) if e.amount else None,
        "applyDate": e.apply_date.isoformat() if e.apply_date else None,
        "description": e.description, "attachments": e.attachments,
        "status": e.status, "approverId": e.approver_id,
    }


def _outsource_dict(o: CostOutsource) -> dict[str, object]:
    return {
        "outsourceId": o.outsource_id, "projectId": o.project_id,
        "vendorName": o.vendor_name,
        "contractAmount": float(o.contract_amount) if o.contract_amount else None,
        "paidAmount": float(o.paid_amount) if o.paid_amount else None,
        "status": o.status,
    }


def _settlement_dict(s: CostSettlement) -> dict[str, object]:
    return {
        "settlementId": s.settlement_id, "projectId": s.project_id,
        "settlementAmount": float(s.settlement_amount) if s.settlement_amount else None,
        "settlementDate": s.settlement_date.isoformat() if s.settlement_date else None,
        "status": s.status, "createdBy": s.created_by,
    }
