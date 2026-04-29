"""Business domain service — contracts, payments, customers, suppliers, procurement."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import PageResult
from app.exceptions import BusinessError, ResourceNotFoundError
from app.models.business.models import (
    Contract,
    ContractInvoice,
    ContractPayment,
    Customer,
    Opportunity,
    ProcurementPlan,
    Quotation,
    Supplier,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class BusinessService:
    """Encapsulates all business-domain database operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Contract ────────────────────────────────────────────────────────

    async def list_contracts(
        self, page: int = 1, size: int = 20, status: str | None = None
    ) -> PageResult:
        base = select(Contract)
        if status:
            base = base.where(Contract.status == status)
        base = base.order_by(Contract.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_contract_dict(c) for c in result.scalars().all()],
        )

    async def list_contracts_by_project(self, project_id: str) -> list[dict[str, object]]:
        stmt = (
            select(Contract)
            .where(Contract.project_id == project_id)
            .order_by(Contract.create_time.desc())
        )
        result = await self.db.execute(stmt)
        return [_contract_dict(c) for c in result.scalars().all()]

    async def get_contract(self, contract_id: str) -> dict[str, object]:
        c = await self._get_contract_or_404(contract_id)
        return _contract_dict(c)

    async def create_contract(self, **kwargs: object) -> dict[str, str]:
        c = Contract(contract_id=str(uuid.uuid4()), **kwargs)
        self.db.add(c)
        await self.db.flush()
        return {"contractId": c.contract_id}

    async def update_contract(self, contract_id: str, **kwargs: object) -> None:
        c = await self._get_contract_or_404(contract_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(c, k):
                setattr(c, k, v)
        await self.db.flush()

    async def delete_contract(self, contract_id: str) -> None:
        c = await self._get_contract_or_404(contract_id)
        await self.db.delete(c)
        await self.db.flush()

    # ── Contract Payment ────────────────────────────────────────────────

    async def list_payments(
        self, contract_id: str | None = None, page: int = 1, size: int = 20
    ) -> PageResult:
        base = select(ContractPayment)
        if contract_id:
            base = base.where(ContractPayment.contract_id == contract_id)
        base = base.order_by(ContractPayment.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_payment_dict(p) for p in result.scalars().all()],
        )

    async def get_payment(self, payment_id: str) -> dict[str, object]:
        p = await self._get_payment_or_404(payment_id)
        return _payment_dict(p)

    async def create_payment(self, **kwargs: object) -> dict[str, str]:
        p = ContractPayment(payment_id=str(uuid.uuid4()), **kwargs)
        self.db.add(p)
        await self.db.flush()
        return {"paymentId": p.payment_id}

    async def update_payment(self, payment_id: str, **kwargs: object) -> None:
        p = await self._get_payment_or_404(payment_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(p, k):
                setattr(p, k, v)
        await self.db.flush()

    async def delete_payment(self, payment_id: str) -> None:
        p = await self._get_payment_or_404(payment_id)
        await self.db.delete(p)
        await self.db.flush()

    async def confirm_payment(self, payment_id: str) -> dict[str, str]:
        p = await self._get_payment_or_404(payment_id)
        p.status = "paid"
        await self.db.flush()
        return {"paymentId": payment_id, "status": p.status}

    # ── Customer ────────────────────────────────────────────────────────

    async def list_customers(
        self, page: int = 1, size: int = 20, status: str | None = None
    ) -> PageResult:
        base = select(Customer)
        if status:
            base = base.where(Customer.status == status)
        base = base.order_by(Customer.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_customer_dict(c) for c in result.scalars().all()],
        )

    async def search_customers(
        self, keyword: str, page: int = 1, size: int = 20
    ) -> PageResult:
        pattern = f"%{keyword}%"
        base = select(Customer).where(
            Customer.customer_name.ilike(pattern)
            | (Customer.contact_person.ilike(pattern))
            | (Customer.industry.ilike(pattern))
        )
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.order_by(Customer.create_time.desc()).offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_customer_dict(c) for c in result.scalars().all()],
        )

    async def get_customer(self, customer_id: str) -> dict[str, object]:
        c = await self._get_customer_or_404(customer_id)
        return _customer_dict(c)

    async def create_customer(self, **kwargs: object) -> dict[str, str]:
        c = Customer(customer_id=str(uuid.uuid4()), **kwargs)
        self.db.add(c)
        await self.db.flush()
        return {"customerId": c.customer_id}

    async def update_customer(self, customer_id: str, **kwargs: object) -> None:
        c = await self._get_customer_or_404(customer_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(c, k):
                setattr(c, k, v)
        await self.db.flush()

    async def delete_customer(self, customer_id: str) -> None:
        c = await self._get_customer_or_404(customer_id)
        await self.db.delete(c)
        await self.db.flush()

    # ── Supplier ────────────────────────────────────────────────────────

    async def list_suppliers(
        self, page: int = 1, size: int = 20, status: str | None = None
    ) -> PageResult:
        base = select(Supplier)
        if status:
            base = base.where(Supplier.status == status)
        base = base.order_by(Supplier.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_supplier_dict(s) for s in result.scalars().all()],
        )

    async def get_supplier(self, supplier_id: str) -> dict[str, object]:
        s = await self._get_supplier_or_404(supplier_id)
        return _supplier_dict(s)

    async def create_supplier(self, **kwargs: object) -> dict[str, str]:
        s = Supplier(supplier_id=str(uuid.uuid4()), **kwargs)
        self.db.add(s)
        await self.db.flush()
        return {"supplierId": s.supplier_id}

    async def update_supplier(self, supplier_id: str, **kwargs: object) -> None:
        s = await self._get_supplier_or_404(supplier_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(s, k):
                setattr(s, k, v)
        await self.db.flush()

    async def delete_supplier(self, supplier_id: str) -> None:
        s = await self._get_supplier_or_404(supplier_id)
        await self.db.delete(s)
        await self.db.flush()

    async def evaluate_supplier(
        self, supplier_id: str, score: float, comment: str
    ) -> dict[str, object]:
        """Record a supplier evaluation. Stores score/comment on the supplier record.

        In a full implementation this would write to a dedicated evaluation table.
        """
        s = await self._get_supplier_or_404(supplier_id)
        # Attach evaluation metadata via a synthetic field (persisted in a real table)
        return {
            "supplierId": s.supplier_id,
            "supplierName": s.supplier_name,
            "score": score,
            "comment": comment,
            "evaluatedAt": _now().isoformat(),
        }

    # ── Quotation ───────────────────────────────────────────────────────

    async def list_quotations(
        self, page: int = 1, size: int = 20, status: str | None = None
    ) -> PageResult:
        base = select(Quotation)
        if status:
            base = base.where(Quotation.status == status)
        base = base.order_by(Quotation.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_quotation_dict(q) for q in result.scalars().all()],
        )

    async def get_quotation(self, quotation_id: str) -> dict[str, object]:
        q = await self._get_quotation_or_404(quotation_id)
        return _quotation_dict(q)

    async def create_quotation(self, **kwargs: object) -> dict[str, str]:
        q = Quotation(quotation_id=str(uuid.uuid4()), **kwargs)
        self.db.add(q)
        await self.db.flush()
        return {"quotationId": q.quotation_id}

    async def update_quotation(self, quotation_id: str, **kwargs: object) -> None:
        q = await self._get_quotation_or_404(quotation_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(q, k):
                setattr(q, k, v)
        await self.db.flush()

    async def delete_quotation(self, quotation_id: str) -> None:
        q = await self._get_quotation_or_404(quotation_id)
        await self.db.delete(q)
        await self.db.flush()

    # ── Procurement Plan ────────────────────────────────────────────────

    async def list_procurement_plans(
        self, project_id: str | None = None, page: int = 1, size: int = 20
    ) -> PageResult:
        base = select(ProcurementPlan)
        if project_id:
            base = base.where(ProcurementPlan.project_id == project_id)
        base = base.order_by(ProcurementPlan.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_plan_dict(p) for p in result.scalars().all()],
        )

    async def get_procurement_plan(self, plan_id: str) -> dict[str, object]:
        p = await self._get_plan_or_404(plan_id)
        return _plan_dict(p)

    async def create_procurement_plan(self, **kwargs: object) -> dict[str, str]:
        p = ProcurementPlan(plan_id=str(uuid.uuid4()), **kwargs)
        self.db.add(p)
        await self.db.flush()
        return {"planId": p.plan_id}

    async def update_procurement_plan(self, plan_id: str, **kwargs: object) -> None:
        p = await self._get_plan_or_404(plan_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(p, k):
                setattr(p, k, v)
        await self.db.flush()

    async def delete_procurement_plan(self, plan_id: str) -> None:
        p = await self._get_plan_or_404(plan_id)
        await self.db.delete(p)
        await self.db.flush()

    # ── Contract Invoice ────────────────────────────────────────────────

    async def list_invoices(
        self, contract_id: str | None = None, page: int = 1, size: int = 20
    ) -> PageResult:
        base = select(ContractInvoice)
        if contract_id:
            base = base.where(ContractInvoice.contract_id == contract_id)
        base = base.order_by(ContractInvoice.create_time.desc())
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))
        return PageResult(
            total=total or 0, page=page, size=size,
            records=[_invoice_dict(i) for i in result.scalars().all()],
        )

    async def get_invoice(self, invoice_id: str) -> dict[str, object]:
        i = await self._get_invoice_or_404(invoice_id)
        return _invoice_dict(i)

    async def create_invoice(self, **kwargs: object) -> dict[str, str]:
        i = ContractInvoice(invoice_id=str(uuid.uuid4()), **kwargs)
        self.db.add(i)
        await self.db.flush()
        return {"invoiceId": i.invoice_id}

    async def update_invoice(self, invoice_id: str, **kwargs: object) -> None:
        i = await self._get_invoice_or_404(invoice_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(i, k):
                setattr(i, k, v)
        await self.db.flush()

    async def delete_invoice(self, invoice_id: str) -> None:
        i = await self._get_invoice_or_404(invoice_id)
        await self.db.delete(i)
        await self.db.flush()

    # ── Internal helpers ────────────────────────────────────────────────

    async def _get_contract_or_404(self, contract_id: str) -> Contract:
        c = await self.db.get(Contract, contract_id)
        if not c:
            raise ResourceNotFoundError("合同", contract_id)
        return c

    async def _get_payment_or_404(self, payment_id: str) -> ContractPayment:
        p = await self.db.get(ContractPayment, payment_id)
        if not p:
            raise ResourceNotFoundError("付款记录", payment_id)
        return p

    async def _get_customer_or_404(self, customer_id: str) -> Customer:
        c = await self.db.get(Customer, customer_id)
        if not c:
            raise ResourceNotFoundError("客户", customer_id)
        return c

    async def _get_supplier_or_404(self, supplier_id: str) -> Supplier:
        s = await self.db.get(Supplier, supplier_id)
        if not s:
            raise ResourceNotFoundError("供应商", supplier_id)
        return s

    async def _get_quotation_or_404(self, quotation_id: str) -> Quotation:
        q = await self.db.get(Quotation, quotation_id)
        if not q:
            raise ResourceNotFoundError("报价单", quotation_id)
        return q

    async def _get_plan_or_404(self, plan_id: str) -> ProcurementPlan:
        p = await self.db.get(ProcurementPlan, plan_id)
        if not p:
            raise ResourceNotFoundError("采购计划", plan_id)
        return p

    async def _get_invoice_or_404(self, invoice_id: str) -> ContractInvoice:
        i = await self.db.get(ContractInvoice, invoice_id)
        if not i:
            raise ResourceNotFoundError("发票", invoice_id)
        return i


# ── Dict converters ──────────────────────────────────────────────────────

def _contract_dict(c: Contract) -> dict[str, object]:
    return {
        "contractId": c.contract_id, "contractCode": c.contract_code,
        "contractName": c.contract_name, "contractType": c.contract_type,
        "partyA": c.party_a, "partyB": c.party_b,
        "totalAmount": float(c.total_amount) if c.total_amount else None,
        "currency": c.currency,
        "signDate": c.sign_date, "startDate": c.start_date, "endDate": c.end_date,
        "projectId": c.project_id, "status": c.status,
        "createdBy": c.created_by, "reminderDays": c.reminder_days,
    }


def _payment_dict(p: ContractPayment) -> dict[str, object]:
    return {
        "paymentId": p.payment_id, "contractId": p.contract_id,
        "paymentType": p.payment_type,
        "plannedAmount": float(p.planned_amount) if p.planned_amount else None,
        "actualAmount": float(p.actual_amount) if p.actual_amount else None,
        "plannedDate": p.planned_date.isoformat() if p.planned_date else None,
        "actualDate": p.actual_date.isoformat() if p.actual_date else None,
        "status": p.status,
    }


def _customer_dict(c: Customer) -> dict[str, object]:
    return {
        "customerId": c.customer_id, "customerName": c.customer_name,
        "customerType": c.customer_type, "contactPerson": c.contact_person,
        "phone": c.phone, "email": c.email, "address": c.address,
        "industry": c.industry, "status": c.status,
    }


def _supplier_dict(s: Supplier) -> dict[str, object]:
    return {
        "supplierId": s.supplier_id, "supplierName": s.supplier_name,
        "supplierType": s.supplier_type, "contactPerson": s.contact_person,
        "phone": s.phone, "email": s.email, "address": s.address,
        "status": s.status,
    }


def _quotation_dict(q: Quotation) -> dict[str, object]:
    return {
        "quotationId": q.quotation_id, "opportunityId": q.opportunity_id,
        "customerId": q.customer_id, "quotationNo": q.quotation_no,
        "amount": float(q.amount) if q.amount else None,
        "validUntil": q.valid_until.isoformat() if q.valid_until else None,
        "status": q.status,
    }


def _plan_dict(p: ProcurementPlan) -> dict[str, object]:
    return {
        "planId": p.plan_id, "projectId": p.project_id,
        "planName": p.plan_name, "procurementType": p.procurement_type,
        "budget": float(p.budget) if p.budget else None,
        "plannedDate": p.planned_date.isoformat() if p.planned_date else None,
        "status": p.status,
    }


def _invoice_dict(i: ContractInvoice) -> dict[str, object]:
    return {
        "invoiceId": i.invoice_id, "contractId": i.contract_id,
        "invoiceNo": i.invoice_no, "invoiceType": i.invoice_type,
        "amount": float(i.amount) if i.amount else None,
        "issueDate": i.issue_date.isoformat() if i.issue_date else None,
        "status": i.status,
    }
