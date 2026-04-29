"""Business API router — consolidates 7 business controllers."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ApiResponse, PageResult
from app.database import get_db
from app.exceptions import ResourceNotFoundError
from app.models.business.models import (
    Contract, ContractPayment, Customer, Opportunity,
    ProcurementPlan, Quotation, Supplier,
)

router = APIRouter(tags=["business"])


# ── Contracts ────────────────────────────────────────────────────────

@router.get("/contracts")
async def list_contracts(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    status: str | None = None, project_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Contract).order_by(Contract.create_time.desc())
    if status:
        stmt = stmt.where(Contract.status == status)
    if project_id:
        stmt = stmt.where(Contract.project_id == project_id)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[_contract_to_dict(c) for c in items],
    ))


@router.post("/contracts")
async def create_contract(req: ContractCreateRequest, db: AsyncSession = Depends(get_db)):
    contract = Contract(
        contract_id=str(uuid.uuid4()), contract_code=req.contract_code,
        contract_name=req.contract_name, contract_type=req.contract_type,
        party_a=req.party_a, party_b=req.party_b, total_amount=req.total_amount,
        currency=req.currency, sign_date=req.sign_date, start_date=req.start_date,
        end_date=req.end_date, project_id=req.project_id,
        status=req.status or "draft", created_by=req.created_by,
        reminder_days=req.reminder_days,
    )
    db.add(contract)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"contractId": contract.contract_id})


@router.put("/contracts/{contract_id}")
async def update_contract(contract_id: str, req: ContractUpdateRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Contract).where(Contract.contract_id == contract_id)
    c = (await db.execute(stmt)).scalar_one_or_none()
    if not c:
        raise ResourceNotFoundError("合同", contract_id)
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/contracts/{contract_id}")
async def delete_contract(contract_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Contract).where(Contract.contract_id == contract_id)
    c = (await db.execute(stmt)).scalar_one_or_none()
    if not c:
        raise ResourceNotFoundError("合同", contract_id)
    await db.delete(c)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Payments ─────────────────────────────────────────────────────────

@router.get("/contracts/{contract_id}/payments")
async def list_payments(contract_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ContractPayment).where(ContractPayment.contract_id == contract_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"paymentId": p.payment_id, "contractId": p.contract_id, "paymentType": p.payment_type,
         "plannedAmount": float(p.planned_amount) if p.planned_amount else None,
         "actualAmount": float(p.actual_amount) if p.actual_amount else None,
         "plannedDate": str(p.planned_date) if p.planned_date else None,
         "actualDate": str(p.actual_date) if p.actual_date else None, "status": p.status} for p in items
    ])


@router.post("/contracts/{contract_id}/payments")
async def create_payment(contract_id: str, req: PaymentCreateRequest, db: AsyncSession = Depends(get_db)):
    payment = ContractPayment(
        payment_id=str(uuid.uuid4()), contract_id=contract_id,
        payment_type=req.payment_type, planned_amount=req.planned_amount,
        actual_amount=req.actual_amount, planned_date=req.planned_date,
        actual_date=req.actual_date, status=req.status or "pending",
    )
    db.add(payment)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"paymentId": payment.payment_id})


# ── Customers ────────────────────────────────────────────────────────

@router.get("/customers")
async def list_customers(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Customer).order_by(Customer.create_time.desc())
    total = (await db.execute(select(func.count()).select_from(Customer))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{"customerId": c.customer_id, "customerName": c.customer_name,
                 "customerType": c.customer_type, "contactPerson": c.contact_person,
                 "phone": c.phone, "email": c.email, "address": c.address,
                 "industry": c.industry, "status": c.status} for c in items],
    ))


@router.post("/customers")
async def create_customer(req: CustomerCreateRequest, db: AsyncSession = Depends(get_db)):
    c = Customer(
        customer_id=str(uuid.uuid4()), customer_name=req.customer_name,
        customer_type=req.customer_type, contact_person=req.contact_person,
        phone=req.phone, email=req.email, address=req.address,
        industry=req.industry, status=req.status or "active",
    )
    db.add(c)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"customerId": c.customer_id})


# ── Suppliers ────────────────────────────────────────────────────────

@router.get("/suppliers")
async def list_suppliers(page: int = 1, size: int = 10, db: AsyncSession = Depends(get_db)):
    stmt = select(Supplier).order_by(Supplier.create_time.desc())
    total = (await db.execute(select(func.count()).select_from(Supplier))).scalar() or 0
    result = await db.execute(stmt.offset((page - 1) * size).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{"supplierId": s.supplier_id, "supplierName": s.supplier_name,
                 "supplierType": s.supplier_type, "contactPerson": s.contact_person,
                 "phone": s.phone, "email": s.email, "address": s.address,
                 "status": s.status} for s in items],
    ))


@router.post("/suppliers")
async def create_supplier(req: SupplierCreateRequest, db: AsyncSession = Depends(get_db)):
    s = Supplier(
        supplier_id=str(uuid.uuid4()), supplier_name=req.supplier_name,
        supplier_type=req.supplier_type, contact_person=req.contact_person,
        phone=req.phone, email=req.email, address=req.address,
        status=req.status or "active",
    )
    db.add(s)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"supplierId": s.supplier_id})


# ── Opportunities ────────────────────────────────────────────────────

@router.get("/opportunities")
async def list_opportunities(page: int = 1, size: int = 10, db: AsyncSession = Depends(get_db)):
    stmt = select(Opportunity).order_by(Opportunity.create_time.desc())
    total = (await db.execute(select(func.count()).select_from(Opportunity))).scalar() or 0
    result = await db.execute(stmt.offset((page - 1) * size).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{"opportunityId": o.opportunity_id, "opportunityName": o.opportunity_name,
                 "customerId": o.customer_id, "expectedAmount": float(o.expected_amount) if o.expected_amount else None,
                 "probability": o.probability, "stage": o.stage, "ownerId": o.owner_id,
                 "expectedCloseDate": str(o.expected_close_date) if o.expected_close_date else None,
                 "status": o.status} for o in items],
    ))


@router.post("/opportunities")
async def create_opportunity(req: OpportunityCreateRequest, db: AsyncSession = Depends(get_db)):
    o = Opportunity(
        opportunity_id=str(uuid.uuid4()), opportunity_name=req.opportunity_name,
        customer_id=req.customer_id, expected_amount=req.expected_amount,
        probability=req.probability, stage=req.stage, owner_id=req.owner_id,
        expected_close_date=req.expected_close_date, status=req.status or "open",
    )
    db.add(o)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"opportunityId": o.opportunity_id})


# ── Quotations ───────────────────────────────────────────────────────

@router.get("/quotations")
async def list_quotations(customer_id: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Quotation)
    if customer_id:
        stmt = stmt.where(Quotation.customer_id == customer_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"quotationId": q.quotation_id, "opportunityId": q.opportunity_id,
         "customerId": q.customer_id, "quotationNo": q.quotation_no,
         "amount": float(q.amount) if q.amount else None,
         "validUntil": str(q.valid_until) if q.valid_until else None, "status": q.status} for q in items
    ])


@router.post("/quotations")
async def create_quotation(req: QuotationCreateRequest, db: AsyncSession = Depends(get_db)):
    q = Quotation(
        quotation_id=str(uuid.uuid4()), opportunity_id=req.opportunity_id,
        customer_id=req.customer_id, quotation_no=req.quotation_no,
        amount=req.amount, valid_until=req.valid_until, status=req.status or "draft",
    )
    db.add(q)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"quotationId": q.quotation_id})


# ── Procurement Plans ────────────────────────────────────────────────

@router.get("/procurement")
async def list_procurement(project_id: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(ProcurementPlan)
    if project_id:
        stmt = stmt.where(ProcurementPlan.project_id == project_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"planId": p.plan_id, "projectId": p.project_id, "planName": p.plan_name,
         "procurementType": p.procurement_type, "budget": float(p.budget) if p.budget else None,
         "plannedDate": str(p.planned_date) if p.planned_date else None, "status": p.status} for p in items
    ])


@router.post("/procurement")
async def create_procurement(req: ProcurementCreateRequest, db: AsyncSession = Depends(get_db)):
    p = ProcurementPlan(
        plan_id=str(uuid.uuid4()), project_id=req.project_id,
        plan_name=req.plan_name, procurement_type=req.procurement_type,
        budget=req.budget, planned_date=req.planned_date, status=req.status or "draft",
    )
    db.add(p)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"planId": p.plan_id})


# ── Legacy aliases (frontend compatibility) ──────────────────────────

@router.get("/contract/list")
async def list_contracts_alias(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    status: str | None = None, project_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await list_contracts(page=page, size=size, status=status, project_id=project_id, db=db)


@router.post("/contract/create")
async def create_contract_alias(req: ContractCreateRequest, db: AsyncSession = Depends(get_db)):
    return await create_contract(req, db)


@router.post("/payment/create")
async def create_payment_alias(contract_id: str, req: PaymentCreateRequest, db: AsyncSession = Depends(get_db)):
    return await create_payment(contract_id, req, db)


@router.post("/payment/{payment_id}/confirm")
async def confirm_payment(payment_id: str, db: AsyncSession = Depends(get_db)):
    from app.exceptions import ResourceNotFoundError
    p = await db.get(ContractPayment, payment_id)
    if not p:
        raise ResourceNotFoundError("Payment", payment_id)
    p.status = "completed"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.get("/payment/list")
async def list_payments_alias(
    contract_id: str | None = None, db: AsyncSession = Depends(get_db),
):
    return await list_payments(contract_id or "", db)


@router.get("/supplier/list")
async def list_suppliers_alias(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    return await list_suppliers(page=page, size=size, db=db)


@router.post("/supplier/create")
async def create_supplier_alias(req: SupplierCreateRequest, db: AsyncSession = Depends(get_db)):
    return await create_supplier(req, db)


# ── Helpers ──────────────────────────────────────────────────────────

def _contract_to_dict(c: Contract) -> dict:
    return {
        "contractId": c.contract_id, "contractCode": c.contract_code,
        "contractName": c.contract_name, "contractType": c.contract_type,
        "partyA": c.party_a, "partyB": c.party_b,
        "totalAmount": float(c.total_amount) if c.total_amount else None,
        "currency": c.currency, "signDate": c.sign_date,
        "startDate": c.start_date, "endDate": c.end_date,
        "projectId": c.project_id, "status": c.status,
        "createdBy": c.created_by, "reminderDays": c.reminder_days,
    }


# ── Request schemas ──────────────────────────────────────────────────

class ContractCreateRequest(BaseModel):
    contract_code: str | None = None
    contract_name: str
    contract_type: str | None = None
    party_a: str | None = None
    party_b: str | None = None
    total_amount: float | None = None
    currency: str | None = None
    sign_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    project_id: str | None = None
    status: str | None = None
    created_by: str | None = None
    reminder_days: int | None = None

class ContractUpdateRequest(BaseModel):
    contract_name: str | None = None
    contract_type: str | None = None
    party_a: str | None = None
    party_b: str | None = None
    total_amount: float | None = None
    currency: str | None = None
    sign_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    status: str | None = None
    reminder_days: int | None = None

class PaymentCreateRequest(BaseModel):
    payment_type: str | None = None
    planned_amount: float | None = None
    actual_amount: float | None = None
    planned_date: datetime | None = None
    actual_date: datetime | None = None
    status: str | None = None

class CustomerCreateRequest(BaseModel):
    customer_name: str
    customer_type: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    industry: str | None = None
    status: str | None = None

class SupplierCreateRequest(BaseModel):
    supplier_name: str
    supplier_type: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    status: str | None = None

class OpportunityCreateRequest(BaseModel):
    opportunity_name: str
    customer_id: str | None = None
    expected_amount: float | None = None
    probability: int | None = None
    stage: str | None = None
    owner_id: str | None = None
    expected_close_date: datetime | None = None
    status: str | None = None

class QuotationCreateRequest(BaseModel):
    opportunity_id: str | None = None
    customer_id: str | None = None
    quotation_no: str | None = None
    amount: float | None = None
    valid_until: datetime | None = None
    status: str | None = None

class ProcurementCreateRequest(BaseModel):
    project_id: str
    plan_name: str
    procurement_type: str | None = None
    budget: float | None = None
    planned_date: datetime | None = None
    status: str | None = None


# ── F-809: Invoice Management ────────────────────────────────────────

@router.get("/invoices")
async def list_invoices(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    contract_id: str | None = None, status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """发票管理列表 (F-809)."""
    from app.models.business.models import ContractInvoice
    stmt = select(ContractInvoice).order_by(ContractInvoice.create_time.desc())
    if contract_id:
        stmt = stmt.where(ContractInvoice.contract_id == contract_id)
    if status:
        stmt = stmt.where(ContractInvoice.status == status)
    result = await db.execute(stmt.offset((page - 1) * size).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"invoiceId": i.invoice_id, "contractId": i.contract_id, "invoiceNo": i.invoice_no,
         "invoiceType": i.invoice_type, "amount": float(i.amount) if i.amount else None,
         "issueDate": str(i.issue_date) if i.issue_date else None, "status": i.status}
        for i in items
    ])


@router.post("/invoices")
async def create_invoice(req: InvoiceCreateRequest, db: AsyncSession = Depends(get_db)):
    """创建发票 (F-809)."""
    from app.models.business.models import ContractInvoice
    inv = ContractInvoice(
        invoice_id=str(uuid.uuid4()), contract_id=req.contract_id,
        invoice_no=req.invoice_no, invoice_type=req.invoice_type,
        amount=req.amount, issue_date=req.issue_date, status=req.status or "pending",
    )
    db.add(inv)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"invoiceId": inv.invoice_id})


# ── F-814: Supplier Evaluation ───────────────────────────────────────

@router.post("/supplier/{supplier_id}/evaluate")
async def evaluate_supplier(supplier_id: str, req: SupplierEvaluateRequest, db: AsyncSession = Depends(get_db)):
    """供应商评估 (F-814)."""
    supplier = await db.get(Supplier, supplier_id)
    if not supplier:
        raise ResourceNotFoundError("供应商", supplier_id)
    score = (req.quality_score * 0.3 + req.delivery_score * 0.25 +
             req.price_score * 0.2 + req.service_score * 0.15 + req.compliance_score * 0.1)
    return ApiResponse(code="SUCCESS", message="success", data={
        "supplierId": supplier_id,
        "supplierName": supplier.supplier_name,
        "totalScore": round(score, 2),
        "breakdown": {
            "quality": req.quality_score,
            "delivery": req.delivery_score,
            "price": req.price_score,
            "service": req.service_score,
            "compliance": req.compliance_score,
        },
        "rating": "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D",
    })


# ── Contract Lifecycle Extensions ────────────────────────────────────

@router.get("/contracts/expiring")
async def list_expiring_contracts(
    days: int = Query(default=30),
    db: AsyncSession = Depends(get_db),
):
    """List contracts expiring within N days."""
    from datetime import date, timedelta
    threshold = date.today() + timedelta(days=days)
    stmt = select(Contract).where(
        Contract.status == "active",
        Contract.end_date <= threshold,
    ).order_by(Contract.end_date.asc())
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data={
        "count": len(items),
        "contracts": [_contract_to_dict(c) for c in items],
    })


@router.post("/contracts/{contract_id}/archive")
async def archive_contract(contract_id: str, db: AsyncSession = Depends(get_db)):
    """Archive a contract."""
    c = await db.get(Contract, contract_id)
    if not c:
        raise ResourceNotFoundError("合同", contract_id)
    c.status = "archived"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.post("/contracts/{contract_id}/terminate")
async def terminate_contract(
    contract_id: str, req: ContractTerminateRequest, db: AsyncSession = Depends(get_db),
):
    """Terminate a contract with reason."""
    c = await db.get(Contract, contract_id)
    if not c:
        raise ResourceNotFoundError("合同", contract_id)
    c.status = "terminated"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Quotation Workflow ───────────────────────────────────────────────

@router.post("/quotations/{quotation_id}/send")
async def send_quotation(quotation_id: str, db: AsyncSession = Depends(get_db)):
    """Send quotation to customer."""
    q = await db.get(Quotation, quotation_id)
    if not q:
        raise ResourceNotFoundError("报价单", quotation_id)
    q.status = "sent"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.post("/quotations/{quotation_id}/accept")
async def accept_quotation(quotation_id: str, db: AsyncSession = Depends(get_db)):
    """Accept quotation."""
    q = await db.get(Quotation, quotation_id)
    if not q:
        raise ResourceNotFoundError("报价单", quotation_id)
    q.status = "accepted"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.post("/quotations/{quotation_id}/reject")
async def reject_quotation(
    quotation_id: str, req: QuotationRejectRequest, db: AsyncSession = Depends(get_db),
):
    """Reject quotation with reason."""
    q = await db.get(Quotation, quotation_id)
    if not q:
        raise ResourceNotFoundError("报价单", quotation_id)
    q.status = "rejected"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Customer Search ──────────────────────────────────────────────────

@router.get("/customers/search")
async def search_customers(
    keyword: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Search customers by name or industry."""
    stmt = select(Customer).where(
        Customer.customer_name.ilike(f"%{keyword}%")
        | Customer.industry.ilike(f"%{keyword}%")
    )
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"customerId": c.customer_id, "customerName": c.customer_name,
         "customerType": c.customer_type, "industry": c.industry,
         "status": c.status} for c in items
    ])


@router.get("/customers/by-industry")
async def group_customers_by_industry(
    industry: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """List customers by industry."""
    stmt = select(Customer).where(Customer.industry == industry)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"customerId": c.customer_id, "customerName": c.customer_name,
         "contactPerson": c.contact_person, "status": c.status} for c in items
    ])


# ── Supplier Blacklist ───────────────────────────────────────────────

@router.post("/suppliers/{supplier_id}/blacklist")
async def blacklist_supplier(
    supplier_id: str, req: SupplierBlacklistRequest, db: AsyncSession = Depends(get_db),
):
    """Add supplier to blacklist."""
    s = await db.get(Supplier, supplier_id)
    if not s:
        raise ResourceNotFoundError("供应商", supplier_id)
    s.status = "blacklisted"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.get("/suppliers/blacklisted")
async def list_blacklisted_suppliers(db: AsyncSession = Depends(get_db)):
    """List blacklisted suppliers."""
    stmt = select(Supplier).where(Supplier.status == "blacklisted")
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"supplierId": s.supplier_id, "supplierName": s.supplier_name,
         "contactPerson": s.contact_person, "phone": s.phone} for s in items
    ])


# ── Payment Plan ─────────────────────────────────────────────────────

@router.get("/payment-plans")
async def list_payment_plans(
    project_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List payment plans."""
    stmt = select(ContractPayment).order_by(ContractPayment.planned_date.desc())
    if project_id:
        stmt = stmt.join(Contract, ContractPayment.contract_id == Contract.contract_id).where(
            Contract.project_id == project_id
        )
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"paymentId": p.payment_id, "contractId": p.contract_id,
         "paymentType": p.payment_type,
         "plannedAmount": float(p.planned_amount) if p.planned_amount else None,
         "plannedDate": str(p.planned_date) if p.planned_date else None,
         "status": p.status} for p in items
    ])


class InvoiceCreateRequest(BaseModel):
    contract_id: str
    invoice_no: str
    invoice_type: str | None = None
    amount: float
    issue_date: datetime | None = None
    status: str | None = None

class SupplierEvaluateRequest(BaseModel):
    quality_score: float = 80.0
    delivery_score: float = 80.0
    price_score: float = 80.0
    service_score: float = 80.0
    compliance_score: float = 80.0


class ContractTerminateRequest(BaseModel):
    reason: str | None = None


class QuotationRejectRequest(BaseModel):
    reason: str | None = None


class SupplierBlacklistRequest(BaseModel):
    reason: str | None = None
