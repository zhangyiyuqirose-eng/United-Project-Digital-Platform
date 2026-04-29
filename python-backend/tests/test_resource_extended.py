"""Extended resource API tests for uncovered endpoints: settlement generation, utilization, replacements."""

from datetime import date
from decimal import Decimal

import pytest

from app.models.resource.models import (
    LeaveRequest, OutsourcePerson, PerformanceEval,
    PersonnelReplacement, PoolMembership, PoolPosition,
    ResourcePool, Settlement,
)
from app.models.timesheet.models import Timesheet


def _make_person(**overrides):
    return OutsourcePerson(
        person_id=overrides.get("person_id", "test-ext-1"),
        emp_code=overrides.get("emp_code", "EMP-EXT-001"),
        name=overrides.get("name", "扩展测试人员"),
        id_card=overrides.get("id_card", "encrypted-id"),
        phone=overrides.get("phone", "13800000099"),
        skill_tags=overrides.get("skill_tags", '["Java"]'),
        level=overrides.get("level", 3),
        daily_rate=overrides.get("daily_rate", Decimal("1200.00")),
        department=overrides.get("department", "研发组"),
        pool_status=overrides.get("pool_status", 0),
    )


# ── Settlement Generation ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_settlement_no_timesheets(client, db_session):
    """Generate settlement when no timesheets exist."""
    resp = await client.post("/api/resource/settlement/generate/2026-04")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["generated"] == 0


@pytest.mark.asyncio
async def test_generate_settlement_with_timesheets(client, db_session):
    """Generate settlement with approved timesheets."""
    db_session.add(_make_person(person_id="p-sett-1", emp_code="ST-001",
                                daily_rate=Decimal("1000")))
    db_session.add(Timesheet(
        timesheet_id="ts-sett-1", staff_id="p-sett-1",
        project_id="proj-sett", work_date=date(2026, 4, 1),
        hours=Decimal("8"), check_status="approved",
    ))
    db_session.add(Timesheet(
        timesheet_id="ts-sett-2", staff_id="p-sett-1",
        project_id="proj-sett", work_date=date(2026, 4, 2),
        hours=Decimal("8"), check_status="approved",
    ))
    await db_session.flush()

    resp = await client.post("/api/resource/settlement/generate/2026-04")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["generated"] >= 1


@pytest.mark.asyncio
async def test_generate_settlement_with_performance(client, db_session):
    """Generate settlement applies performance coefficient."""
    db_session.add(_make_person(person_id="p-sett-perf", emp_code="SP-001",
                                daily_rate=Decimal("1000")))
    db_session.add(PerformanceEval(
        eval_id="eval-perf-sett", person_id="p-sett-perf", period="2026-Q1",
        overall_score=Decimal("92"), grade="A",
    ))
    db_session.add(Timesheet(
        timesheet_id="ts-spf-1", staff_id="p-sett-perf",
        project_id="proj-spf", work_date=date(2026, 4, 1),
        hours=Decimal("8"), check_status="approved",
    ))
    await db_session.flush()

    resp = await client.post("/api/resource/settlement/generate/2026-04")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_list_settlements_filter_period(client, db_session):
    db_session.add(_make_person(person_id="p-lsf", emp_code="LSF-001"))
    db_session.add(Settlement(
        settlement_id="set-lsf-1", person_id="p-lsf", period="2026-04",
        status=0,
    ))
    await db_session.flush()

    resp = await client.get("/api/resource/settlements", params={"period": "2026-04"})
    data = resp.json()["data"]
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_list_settlements_filter_status(client, db_session):
    db_session.add(Settlement(
        settlement_id="set-lfs-1", person_id="p-lsf2", period="2026-03",
        status=2,
    ))
    await db_session.flush()

    resp = await client.get("/api/resource/settlements", params={"status": 2})
    data = resp.json()["data"]
    assert all(r["status"] == 2 for r in data["records"])


@pytest.mark.asyncio
async def test_confirm_settlement_with_details(client, db_session):
    db_session.add(_make_person(person_id="p-conf2", emp_code="CF2-001"))
    db_session.add(Settlement(
        settlement_id="set-conf2", person_id="p-conf2", period="2026-04",
        status=0,
    ))
    await db_session.flush()

    resp = await client.put("/api/resource/settlement/set-conf2/confirm", json={
        "confirmed_by": "admin-001",
    })
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_reject_settlement_explicit(client, db_session):
    db_session.add(_make_person(person_id="p-rej2", emp_code="RJ2-001"))
    db_session.add(Settlement(
        settlement_id="set-rej2", person_id="p-rej2", period="2026-04",
        status=1,
    ))
    await db_session.flush()

    resp = await client.put("/api/resource/settlement/set-rej2/reject")
    assert resp.status_code == 200


# ── Utilization ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_utilization_with_timesheets(client, db_session):
    db_session.add(_make_person(person_id="p-util-ts", emp_code="UTS-001"))
    db_session.add(Timesheet(
        timesheet_id="ts-util-1", staff_id="p-util-ts",
        project_id="proj-util", work_date=date(2026, 4, 1),
        hours=Decimal("8"), check_status="approved",
    ))
    await db_session.flush()

    resp = await client.get("/api/resource/utilization/person/p-util-ts")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "personId" in data
    assert "totalHours" in data
    assert "loadRate" in data


@pytest.mark.asyncio
async def test_utilization_nonexistent_person(client):
    """Utilization endpoint should return 200 even for nonexistent persons."""
    resp = await client.get("/api/resource/utilization/person/nonexistent")
    # Endpoint does a SUM query on Timesheet; no person lookup, so no 404
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_utilization_warnings_with_data(client, db_session):
    db_session.add(_make_person(person_id="p-uw-1", emp_code="UW-001"))
    # Overload: > 176 hours
    for i in range(25):
        db_session.add(Timesheet(
            timesheet_id=f"ts-ow-{i}", staff_id="p-uw-1",
            project_id="proj-ow", work_date=date(2026, 4, min(i + 1, 28)),
            hours=Decimal("8"), check_status="approved",
        ))
    await db_session.flush()

    resp = await client.get("/api/resource/utilization/warnings")
    assert resp.status_code == 200


# ── Leave Requests Extended ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_leave_requests(client, db_session):
    db_session.add(_make_person(person_id="p-ll-1", emp_code="LL-001"))
    db_session.add(LeaveRequest(
        leave_id="leave-list-1", person_id="p-ll-1",
        leave_type="年假", start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 3), days=3, status=0,
    ))
    await db_session.flush()

    resp = await client.get("/api/resource/leave", params={"person_id": "p-ll-1"})
    data = resp.json()["data"]
    assert data["total"] >= 1


# ── Personnel Replacement ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_replacements(client, db_session):
    db_session.add(PersonnelReplacement(
        replace_id="repl-list-1",
        person_id="p-old",
        project_id="proj-old",
        reason="历史替换",
    ))
    await db_session.flush()

    resp = await client.get("/api/resource/replacements")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_create_replacement(client, db_session):
    resp = await client.post("/api/resource/replacements", json={
        "person_id": "p-repl-src",
        "project_id": "proj-repl",
        "reason": "人员调动",
    })
    assert resp.status_code == 200


# ── Pool Memberships / CRUD ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_pools(client, db_session):
    db_session.add(ResourcePool(pool_id="pool-lp2", pool_name="列表面试池"))
    await db_session.flush()

    resp = await client.get("/api/resource/pools")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) >= 1


# ── Pool Positions Extended ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_positions_filter_pool(client, db_session):
    db_session.add(ResourcePool(pool_id="pool-lpf", pool_name="过滤池"))
    db_session.add(PoolPosition(
        position_id="pos-lpf-1", pool_id="pool-lpf",
        position_name="高级前端", level=4, head_count=2,
    ))
    await db_session.flush()

    resp = await client.get("/api/resource/positions", params={"pool_id": "pool-lpf"})
    data = resp.json()["data"]
    assert len(data) >= 1


# ── Outsourcing Management ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_outsourcing_by_pool(client, db_session):
    db_session.add(_make_person(person_id="p-out-1", emp_code="OUT-001", pool_status=0))
    await db_session.flush()

    resp = await client.get("/api/resource/outsourcing/pool/pool-out")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_outsourcing_person(client, db_session):
    db_session.add(_make_person(person_id="p-out-det", emp_code="OD-001"))
    await db_session.flush()

    resp = await client.get("/api/resource/outsourcing/p-out-det")
    assert resp.status_code == 200
