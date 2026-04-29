"""Extended integration tests for /api/business/* endpoints — fills coverage gaps."""

import pytest

from app.models.business.models import (
    Contract, ContractPayment, Customer, Opportunity,
    ProcurementPlan, Quotation, Supplier,
)


# ── Contract CRUD ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_contracts_empty(client):
    resp = await client.get("/api/business/contracts")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_list_contracts_with_data(client, db_session):
    db_session.add(Contract(
        contract_id="ctr-lc-1", contract_code="CTR-001",
        contract_name="List Test", project_id="proj-1",
        party_a="A Corp", party_b="B Corp", total_amount=50000.0,
        status="active",
    ))
    await db_session.flush()

    resp = await client.get("/api/business/contracts", params={"page": 1, "size": 10})
    data = resp.json()["data"]
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_list_contracts_filter_status(client, db_session):
    db_session.add(Contract(
        contract_id="ctr-fs-1", contract_name="Active Ctr",
        party_a="A", party_b="B", status="active",
    ))
    db_session.add(Contract(
        contract_id="ctr-fs-2", contract_name="Draft Ctr",
        party_a="A", party_b="B", status="draft",
    ))
    await db_session.flush()

    resp = await client.get("/api/business/contracts", params={"status": "active"})
    records = resp.json()["data"]["records"]
    assert all(r["status"] == "active" for r in records)


@pytest.mark.asyncio
async def test_list_contracts_filter_project(client, db_session):
    db_session.add(Contract(
        contract_id="ctr-fp-1", contract_name="Project A Ctr",
        party_a="A", party_b="B", project_id="proj-a",
    ))
    await db_session.flush()

    resp = await client.get("/api/business/contracts", params={"project_id": "proj-a"})
    assert resp.json()["data"]["total"] >= 1


@pytest.mark.asyncio
async def test_create_contract(client, db_session):
    resp = await client.post("/api/business/contracts", json={
        "contract_name": "New Contract",
        "contract_code": "CTR-NEW-001",
        "party_a": "Corp A",
        "party_b": "Corp B",
        "total_amount": 100000.0,
    })
    assert resp.status_code == 200
    assert "contractId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_update_contract(client, db_session):
    db_session.add(Contract(
        contract_id="ctr-upd-1", contract_name="Old Name",
        party_a="A", party_b="B", status="draft",
    ))
    await db_session.flush()

    resp = await client.put("/api/business/contracts/ctr-upd-1", json={
        "contract_name": "Updated Name",
        "status": "active",
    })
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_update_contract_not_found(client):
    resp = await client.put("/api/business/contracts/nonexistent", json={
        "contract_name": "X",
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_contract(client, db_session):
    db_session.add(Contract(
        contract_id="ctr-del-1", contract_name="Delete Me",
        party_a="A", party_b="B", status="draft",
    ))
    await db_session.flush()

    resp = await client.delete("/api/business/contracts/ctr-del-1")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_delete_contract_not_found(client):
    resp = await client.delete("/api/business/contracts/nonexistent")
    assert resp.status_code == 404


# ── Payments ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_payments(client, db_session):
    db_session.add(ContractPayment(
        payment_id="pay-lp-1", contract_id="ctr-pay-1",
        payment_type="advance", planned_amount=10000.0,
    ))
    await db_session.flush()

    resp = await client.get("/api/business/contracts/ctr-pay-1/payments")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_create_payment(client, db_session):
    resp = await client.post("/api/business/contracts/ctr-new-1/payments", json={
        "payment_type": "milestone",
        "planned_amount": 25000.0,
    })
    assert resp.status_code == 200
    assert "paymentId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_confirm_payment(client, db_session):
    db_session.add(ContractPayment(
        payment_id="pay-conf-1", contract_id="ctr-1",
        payment_type="advance", planned_amount=5000.0, status="pending",
    ))
    await db_session.flush()

    resp = await client.post("/api/business/payment/pay-conf-1/confirm")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_confirm_payment_not_found(client):
    resp = await client.post("/api/business/payment/nonexistent/confirm")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_payments_alias(client, db_session):
    db_session.add(ContractPayment(
        payment_id="pay-alias-1", contract_id="ctr-alias",
        payment_type="final", planned_amount=30000.0,
    ))
    await db_session.flush()

    resp = await client.get("/api/business/payment/list", params={"contract_id": "ctr-alias"})
    assert resp.status_code == 200


# ── Customers ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_customers_empty(client):
    resp = await client.get("/api/business/customers")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_customer(client, db_session):
    resp = await client.post("/api/business/customers", json={
        "customer_name": "Test Customer",
        "customer_type": "enterprise",
        "industry": "Technology",
    })
    assert resp.status_code == 200
    assert "customerId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_create_customer_minimal(client, db_session):
    resp = await client.post("/api/business/customers", json={
        "customer_name": "Minimal Customer",
    })
    assert resp.status_code == 200


# ── Suppliers ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_suppliers_empty(client):
    resp = await client.get("/api/business/suppliers")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_supplier(client, db_session):
    resp = await client.post("/api/business/suppliers", json={
        "supplier_name": "Test Supplier",
        "contact_person": "Contact",
    })
    assert resp.status_code == 200
    assert "supplierId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_list_suppliers_alias(client, db_session):
    db_session.add(Supplier(
        supplier_id="supp-alias-1", supplier_name="Alias Supplier",
        status="active",
    ))
    await db_session.flush()

    resp = await client.get("/api/business/supplier/list", params={"page": 1, "size": 10})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_supplier_alias(client, db_session):
    resp = await client.post("/api/business/supplier/create", json={
        "supplier_name": "Alias Created Supplier",
        "contact_person": "Contact",
    })
    assert resp.status_code == 200


# ── Opportunities ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_opportunities(client, db_session):
    db_session.add(Opportunity(
        opportunity_id="opp-1", opportunity_name="Big Deal",
        expected_amount=500000.0, probability=60, stage="proposal",
    ))
    await db_session.flush()

    resp = await client.get("/api/business/opportunities")
    data = resp.json()["data"]
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_create_opportunity(client, db_session):
    resp = await client.post("/api/business/opportunities", json={
        "opportunity_name": "New Opportunity",
        "expected_amount": 200000.0,
        "probability": 50,
    })
    assert resp.status_code == 200
    assert "opportunityId" in resp.json()["data"]


# ── Quotations ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_quotations(client, db_session):
    db_session.add(Quotation(
        quotation_id="quote-1", quotation_no="Q-010",
        amount=15000.0, status="draft",
    ))
    await db_session.flush()

    resp = await client.get("/api/business/quotations")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_create_quotation(client, db_session):
    resp = await client.post("/api/business/quotations", json={
        "quotation_no": "Q-020",
        "amount": 30000.0,
    })
    assert resp.status_code == 200
    assert "quotationId" in resp.json()["data"]


# ── Procurement ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_procurement(client, db_session):
    db_session.add(ProcurementPlan(
        plan_id="plan-1", project_id="proj-1",
        plan_name="Hardware Procurement", procurement_type="equipment",
        budget=50000.0,
    ))
    await db_session.flush()

    resp = await client.get("/api/business/procurement", params={"project_id": "proj-1"})
    assert resp.status_code == 200
    assert len(resp.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_create_procurement(client, db_session):
    resp = await client.post("/api/business/procurement", json={
        "project_id": "proj-1",
        "plan_name": "Software Licenses",
        "procurement_type": "software",
        "budget": 20000.0,
    })
    assert resp.status_code == 200
    assert "planId" in resp.json()["data"]


# ── Invoices ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_invoices(client, db_session):
    db_session.add(ContractPayment(
        payment_id="inv-ctr-1", contract_id="ctr-inv",
        payment_type="advance", planned_amount=10000.0,
    ))
    await db_session.flush()

    resp = await client.get("/api/business/invoices")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_invoice(client, db_session):
    resp = await client.post("/api/business/invoices", json={
        "contract_id": "ctr-inv-1",
        "invoice_no": "INV-001",
        "amount": 50000.0,
    })
    assert resp.status_code == 200
    assert "invoiceId" in resp.json()["data"]


# ── Supplier Evaluation ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_evaluate_supplier(client, db_session):
    db_session.add(Supplier(
        supplier_id="supp-eval-1", supplier_name="Eval Supplier",
        status="active",
    ))
    await db_session.flush()

    resp = await client.post("/api/business/supplier/supp-eval-1/evaluate", json={
        "quality_score": 90,
        "delivery_score": 85,
        "price_score": 88,
        "service_score": 92,
        "compliance_score": 95,
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["rating"] == "B"
    assert data["supplierName"] == "Eval Supplier"


@pytest.mark.asyncio
async def test_evaluate_supplier_not_found(client):
    resp = await client.post("/api/business/supplier/nonexistent/evaluate", json={
        "quality_score": 80,
        "delivery_score": 80,
        "price_score": 80,
        "service_score": 80,
        "compliance_score": 80,
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_evaluate_supplier_rating_b(client, db_session):
    db_session.add(Supplier(
        supplier_id="supp-eval-2", supplier_name="B-Rated Supplier",
    ))
    await db_session.flush()

    resp = await client.post("/api/business/supplier/supp-eval-2/evaluate", json={
        "quality_score": 82,
        "delivery_score": 80,
        "price_score": 78,
        "service_score": 85,
        "compliance_score": 80,
    })
    data = resp.json()["data"]
    assert data["rating"] == "B"


# ── Payment Plans ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_payment_plans(client, db_session):
    db_session.add(ContractPayment(
        payment_id="pp-1", contract_id="ctr-pp-1",
        payment_type="advance", planned_amount=10000.0,
    ))
    await db_session.flush()

    resp = await client.get("/api/business/payment-plans")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_list_payment_plans_by_project(client, db_session):
    db_session.add(Contract(
        contract_id="ctr-pp-proj", project_id="proj-pp",
        contract_name="Project Contract", party_a="A", party_b="B",
    ))
    db_session.add(ContractPayment(
        payment_id="pp-proj-1", contract_id="ctr-pp-proj",
        payment_type="milestone", planned_amount=25000.0,
    ))
    await db_session.flush()

    resp = await client.get("/api/business/payment-plans", params={"project_id": "proj-pp"})
    assert resp.status_code == 200


# ── Contract Alias Routes ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_contracts_alias(client, db_session):
    db_session.add(Contract(
        contract_id="ctr-alias-lc", contract_name="Alias List",
        party_a="A", party_b="B", status="active",
    ))
    await db_session.flush()

    resp = await client.get("/api/business/contract/list", params={"page": 1, "size": 10})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_contract_alias(client, db_session):
    resp = await client.post("/api/business/contract/create", json={
        "contract_name": "Alias Created",
        "party_a": "A",
        "party_b": "B",
    })
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_payment_alias(client, db_session):
    resp = await client.post("/api/business/payment/create", params={"contract_id": "ctr-alias-pay"}, json={
        "payment_type": "advance",
        "planned_amount": 1000.0,
    })
    assert resp.status_code == 200
