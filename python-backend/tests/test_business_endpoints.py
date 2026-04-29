"""Integration tests for business service extended endpoints."""

import pytest

from app.models.business.models import Contract, Customer, Quotation, Supplier


# ── Contract Lifecycle ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_expiring_contracts(client, db_session):
    db_session.add(Contract(
        contract_id="ctr-exp-1",
        contract_name="Expiring Contract",
        project_id="proj-1",
        party_a="Test Party A",
        party_b="Test Party B",
        total_amount=50000.0,
        status="active",
        end_date="2026-05-01",
    ))
    await db_session.flush()

    resp = await client.get("/api/business/contracts/expiring")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_archive_contract(client, db_session):
    db_session.add(Contract(
        contract_id="ctr-arch-1",
        contract_name="Archive Contract",
        project_id="proj-1",
        party_a="Test Party A",
        party_b="Test Party B",
        total_amount=30000.0,
        status="completed",
    ))
    await db_session.flush()

    resp = await client.post("/api/business/contracts/ctr-arch-1/archive")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_terminate_contract(client, db_session):
    db_session.add(Contract(
        contract_id="ctr-term-1",
        contract_name="Terminate Contract",
        project_id="proj-1",
        party_a="Test Party A",
        party_b="Test Party B",
        total_amount=80000.0,
        status="active",
    ))
    await db_session.flush()

    resp = await client.post("/api/business/contracts/ctr-term-1/terminate", json={
        "reason": "Mutual agreement",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


# ── Quotation Workflow ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_send_quotation(client, db_session):
    db_session.add(Quotation(
        quotation_id="quote-send-1",
        quotation_no="Q-001",
        status="draft",
    ))
    await db_session.flush()

    resp = await client.post("/api/business/quotations/quote-send-1/send")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_accept_quotation(client, db_session):
    db_session.add(Quotation(
        quotation_id="quote-accept-1",
        quotation_no="Q-002",
        status="sent",
    ))
    await db_session.flush()

    resp = await client.post("/api/business/quotations/quote-accept-1/accept")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_reject_quotation(client, db_session):
    db_session.add(Quotation(
        quotation_id="quote-reject-1",
        quotation_no="Q-003",
        status="sent",
    ))
    await db_session.flush()

    resp = await client.post("/api/business/quotations/quote-reject-1/reject", json={
        "reason": "Price too high",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


# ── Customer Management ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_customers(client, db_session):
    db_session.add(Customer(
        customer_id="cust-search-1",
        customer_name="Search Test Customer",
        industry="Finance",
    ))
    await db_session.flush()

    resp = await client.get("/api/business/customers/search", params={"keyword": "Search"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_customers_by_industry(client, db_session):
    db_session.add(Customer(
        customer_id="cust-ind-1",
        customer_name="Tech Customer A",
        industry="Technology",
    ))
    db_session.add(Customer(
        customer_id="cust-ind-2",
        customer_name="Tech Customer B",
        industry="Technology",
    ))
    await db_session.flush()

    resp = await client.get("/api/business/customers/by-industry", params={"industry": "Technology"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) >= 2


# ── Supplier Management ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_blacklist_supplier(client, db_session):
    db_session.add(Supplier(
        supplier_id="supp-black-1",
        supplier_name="Blacklist Test Supplier",
        contact_person="Test Contact",
        status="active",
    ))
    await db_session.flush()

    resp = await client.post("/api/business/suppliers/supp-black-1/blacklist", json={
        "reason": "Breach of contract",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_list_blacklisted_suppliers(client, db_session):
    db_session.add(Supplier(
        supplier_id="supp-bl-1",
        supplier_name="Blacklisted Supplier",
        contact_person="Test Contact",
        status="blacklisted",
    ))
    await db_session.flush()

    resp = await client.get("/api/business/suppliers/blacklisted")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert any(s["supplierId"] == "supp-bl-1" for s in data)
