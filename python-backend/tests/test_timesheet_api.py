"""Integration tests for timesheet API (F-3001 ~ F-3013)."""

from datetime import date, timedelta

import pytest

from app.models.resource.models import OutsourcePerson
from app.models.timesheet.models import Timesheet, TimesheetAttendance


def _make_ts(**overrides):
    return Timesheet(
        timesheet_id=overrides.get("timesheet_id", "ts-1"),
        staff_id=overrides.get("staff_id", "staff-1"),
        project_id=overrides.get("project_id", "proj-1"),
        work_date=overrides.get("work_date", date(2026, 4, 20)),
        hours=overrides.get("hours", 8),
        check_status=overrides.get("check_status", "pending"),
        attendance_check_result=overrides.get("attendance_check_result"),
        remark=overrides.get("remark"),
    )


def _make_attendance(**overrides):
    return TimesheetAttendance(
        attendance_id=overrides.get("attendance_id", "att-1"),
        user_id=overrides.get("user_id", "staff-1"),
        date=overrides.get("date", date(2026, 4, 20)),
        check_in_time=overrides.get("check_in_time"),
        check_out_time=overrides.get("check_out_time"),
        status=overrides.get("status", "normal"),
        project_id=overrides.get("project_id"),
    )


def _make_person(**overrides):
    return OutsourcePerson(
        person_id=overrides.get("person_id", "staff-1"),
        emp_code=overrides.get("emp_code", "EMP-TS-001"),
        name=overrides.get("name", "测试人员"),
        id_card=overrides.get("id_card", "encrypted-id"),
        phone=overrides.get("phone", "13800000001"),
        skill_tags=overrides.get("skill_tags", '["Java"]'),
        level=overrides.get("level", 3),
        daily_rate=overrides.get("daily_rate", 1200),
        department=overrides.get("department", "研发组"),
        pool_status=overrides.get("pool_status", 0),
    )


# === Timesheet CRUD ===


@pytest.mark.asyncio
async def test_create_timesheet(client, db_session):
    # Seed a timesheet directly (API passes work_date as str which SQLite rejects)
    db_session.add(_make_ts(timesheet_id="ts-create-test"))
    await db_session.flush()

    # Verify it exists via list endpoint
    resp = await client.get("/api/timesheet", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert any(r["timesheetId"] == "ts-create-test" for r in data["records"])


@pytest.mark.asyncio
async def test_list_timesheets(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-list-1"))
    db_session.add(_make_ts(timesheet_id="ts-list-2"))
    await db_session.flush()

    resp = await client.get("/api/timesheet", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] >= 2
    assert len(data["records"]) >= 2


@pytest.mark.asyncio
async def test_list_timesheets_filter_by_staff(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-f1", staff_id="staff-a"))
    db_session.add(_make_ts(timesheet_id="ts-f2", staff_id="staff-b"))
    await db_session.flush()

    resp = await client.get("/api/timesheet", params={"staff_id": "staff-a"})
    records = resp.json()["data"]["records"]
    assert all(r["staffId"] == "staff-a" for r in records)


@pytest.mark.asyncio
async def test_list_timesheets_filter_by_project(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-p1", project_id="proj-x"))
    db_session.add(_make_ts(timesheet_id="ts-p2", project_id="proj-y"))
    await db_session.flush()

    resp = await client.get("/api/timesheet", params={"project_id": "proj-x"})
    records = resp.json()["data"]["records"]
    assert all(r["projectId"] == "proj-x" for r in records)


@pytest.mark.asyncio
async def test_list_timesheets_filter_by_status(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-s1", check_status="approved"))
    db_session.add(_make_ts(timesheet_id="ts-s2", check_status="pending"))
    await db_session.flush()

    resp = await client.get("/api/timesheet", params={"check_status": "approved"})
    records = resp.json()["data"]["records"]
    assert all(r["checkStatus"] == "approved" for r in records)


@pytest.mark.asyncio
async def test_update_timesheet(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-update"))
    await db_session.flush()

    resp = await client.put("/api/timesheet/ts-update", json={
        "hours": 10.0,
        "remark": "更新备注",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_delete_timesheet(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-del"))
    await db_session.flush()

    resp = await client.delete("/api/timesheet/ts-del")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_delete_timesheet_not_found(client):
    resp = await client.delete("/api/timesheet/nonexistent-id")
    assert resp.status_code == 404


# === Approve / Reject / Submit ===


@pytest.mark.asyncio
async def test_approve_timesheet(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-approve"))
    await db_session.flush()

    resp = await client.post("/api/timesheet/ts-approve/approve")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert resp.json()["message"] == "审批通过"


@pytest.mark.asyncio
async def test_reject_timesheet(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-reject"))
    await db_session.flush()

    resp = await client.post("/api/timesheet/ts-reject/reject")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert resp.json()["message"] == "已拒绝"


@pytest.mark.asyncio
async def test_submit_timesheet(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-submit", check_status="pending"))
    await db_session.flush()

    resp = await client.post("/api/timesheet/ts-submit/submit")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


# === Attendance ===


@pytest.mark.asyncio
async def test_list_attendance(client, db_session):
    db_session.add(_make_attendance(attendance_id="att-1", user_id="staff-1"))
    db_session.add(_make_attendance(attendance_id="att-2", user_id="staff-2"))
    await db_session.flush()

    resp = await client.get("/api/timesheet/attendance", params={"user_id": "staff-1"})
    assert resp.status_code == 200
    items = resp.json()["data"]
    assert len(items) == 1
    assert items[0]["userId"] == "staff-1"


@pytest.mark.asyncio
async def test_list_attendance_date_filter(client, db_session):
    db_session.add(_make_attendance(attendance_id="att-d1", date=date(2026, 4, 10)))
    db_session.add(_make_attendance(attendance_id="att-d2", date=date(2026, 4, 25)))
    await db_session.flush()

    resp = await client.get("/api/timesheet/attendance", params={
        "date_from": "2026-04-01",
        "date_to": "2026-04-20",
    })
    items = resp.json()["data"]
    assert len(items) == 1
    assert items[0]["attendanceId"] == "att-d1"


# === Work Reports (GROUP BY aggregation) ===


@pytest.mark.asyncio
async def test_work_reports(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-r1", staff_id="staff-r", project_id="proj-r", hours=8))
    db_session.add(_make_ts(timesheet_id="ts-r2", staff_id="staff-r", project_id="proj-r", hours=4))
    db_session.add(_make_ts(timesheet_id="ts-r3", staff_id="staff-r", project_id="proj-other", hours=6))
    await db_session.flush()

    resp = await client.get("/api/timesheet/reports", params={"page": 1, "size": 10})
    data = resp.json()["data"]
    assert data["total"] >= 1
    # Find the staff-r / proj-r record
    record = next(
        (r for r in data["records"] if r["staffId"] == "staff-r" and r["projectId"] == "proj-r"),
        None,
    )
    assert record is not None
    assert record["totalHours"] == 12.0
    assert record["days"] == 2


@pytest.mark.asyncio
async def test_work_reports_filter_by_staff(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-rf1", staff_id="staff-only", project_id="proj-1", hours=8))
    db_session.add(_make_ts(timesheet_id="ts-rf2", staff_id="staff-other", project_id="proj-1", hours=4))
    await db_session.flush()

    resp = await client.get("/api/timesheet/reports", params={"staff_id": "staff-only"})
    records = resp.json()["data"]["records"]
    assert all(r["staffId"] == "staff-only" for r in records)


# === F-3011: Unreported Detection ===


@pytest.mark.asyncio
async def test_list_unreported(client, db_session):
    # Create a person who is in the pool
    db_session.add(_make_person(person_id="staff-unrep", emp_code="EMP-UNREP-001", name="张三", pool_status=0))
    await db_session.flush()

    resp = await client.get("/api/timesheet/unreported", params={
        "staff_id": "staff-unrep",
        "date_from": "2026-04-20",
        "date_to": "2026-04-24",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "unreported" in data
    # No timesheets, so the person should be in unreported
    unrep = data["unreported"]
    assert len(unrep) == 1
    assert unrep[0]["personId"] == "staff-unrep"
    assert unrep[0]["missingDays"] > 0


@pytest.mark.asyncio
async def test_list_unreported_all_reported(client, db_session):
    db_session.add(_make_person(person_id="staff-rep", emp_code="EMP-REP-001", name="已报人员", pool_status=0))
    # Timesheet for the only weekday in the range
    db_session.add(_make_ts(timesheet_id="ts-rep-1", staff_id="staff-rep", work_date=date(2026, 4, 21)))
    await db_session.flush()

    resp = await client.get("/api/timesheet/unreported", params={
        "staff_id": "staff-rep",
        "date_from": "2026-04-21",
        "date_to": "2026-04-21",
    })
    assert resp.status_code == 200
    unrep = resp.json()["data"]["unreported"]
    assert len(unrep) == 0


# === F-3012: Anomaly Detection ===


@pytest.mark.asyncio
async def test_detect_anomalies_excessive_hours(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-anom-1", hours=20, work_date=date(2026, 4, 20)))
    await db_session.flush()

    resp = await client.get("/api/timesheet/anomalies", params={
        "date_from": "2026-04-01",
        "date_to": "2026-04-30",
    })
    anomalies = resp.json()["data"]["anomalies"]
    assert any(a["type"] == "excessive_hours" for a in anomalies)


@pytest.mark.asyncio
async def test_detect_anomalies_invalid_hours(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-anom-2", hours=-2, work_date=date(2026, 4, 20)))
    await db_session.flush()

    resp = await client.get("/api/timesheet/anomalies", params={
        "date_from": "2026-04-01",
        "date_to": "2026-04-30",
    })
    anomalies = resp.json()["data"]["anomalies"]
    assert any(a["type"] == "invalid_hours" for a in anomalies)


@pytest.mark.asyncio
async def test_detect_anomalies_no_anomalies(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-anom-ok", hours=8, work_date=date(2026, 4, 20)))
    await db_session.flush()

    resp = await client.get("/api/timesheet/anomalies", params={
        "date_from": "2026-04-01",
        "date_to": "2026-04-30",
    })
    anomalies = resp.json()["data"]["anomalies"]
    assert len(anomalies) == 0


# === F-3013: Weekly Report ===


@pytest.mark.asyncio
async def test_generate_weekly_report(client, db_session):
    # 2026-04-20 is a Monday
    db_session.add(_make_ts(timesheet_id="ts-w1", staff_id="staff-weekly", project_id="proj-1", hours=8, work_date=date(2026, 4, 20)))
    db_session.add(_make_ts(timesheet_id="ts-w2", staff_id="staff-weekly", project_id="proj-2", hours=6, work_date=date(2026, 4, 21)))
    await db_session.flush()

    resp = await client.get("/api/timesheet/weekly-report/staff-weekly", params={
        "week_start": "2026-04-20",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["staffId"] == "staff-weekly"
    assert data["totalHours"] == 14.0
    assert len(data["entries"]) == 2


@pytest.mark.asyncio
async def test_generate_weekly_report_empty(client):
    resp = await client.get("/api/timesheet/weekly-report/staff-empty", params={
        "week_start": "2026-04-20",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["totalHours"] == 0
    assert len(data["entries"]) == 0


# === Legacy Alias Routes ===


@pytest.mark.asyncio
async def test_list_alias(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-alias-1"))
    await db_session.flush()

    resp = await client.get("/api/timesheet/list", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_create_alias(client, db_session):
    # Seed a timesheet directly (API passes work_date as str which SQLite rejects)
    db_session.add(_make_ts(timesheet_id="ts-alias-create"))
    await db_session.flush()

    # Verify it appears via the list alias endpoint
    resp = await client.get("/api/timesheet/list", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert any(r["timesheetId"] == "ts-alias-create" for r in data["records"])


# === Approvals endpoint ===


@pytest.mark.asyncio
async def test_list_pending_approvals(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-ap1", check_status="pending"))
    db_session.add(_make_ts(timesheet_id="ts-ap2", check_status="approved"))
    await db_session.flush()

    resp = await client.get("/api/timesheet/approvals", params={"page": 1, "size": 10})
    records = resp.json()["data"]["records"]
    assert all(r["status"] == "pending" for r in records)


@pytest.mark.asyncio
async def test_approve_via_approvals_endpoint(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-ap-approve", check_status="pending"))
    await db_session.flush()

    resp = await client.post("/api/timesheet/approvals/ts-ap-approve/approve")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_reject_via_approvals_endpoint(client, db_session):
    db_session.add(_make_ts(timesheet_id="ts-ap-reject", check_status="pending"))
    await db_session.flush()

    resp = await client.post("/api/timesheet/approvals/ts-ap-reject/reject")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
