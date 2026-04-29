"""Integration tests for resource pool management API (F-501 ~ F-513)."""

from datetime import date
from decimal import Decimal

import pytest

from app.models.resource.models import (
    AttendanceRecord,
    LeaveRequest,
    OutsourcePerson,
    PerformanceEval,
    PersonnelReplacement,
    PoolMembership,
    PoolPosition,
    ResourcePool,
    Settlement,
    SkillProfile,
)


def _make_person(**overrides):
    return OutsourcePerson(
        person_id=overrides.get("person_id", "test-p-1"),
        emp_code=overrides.get("emp_code", "EMP-TEST-001"),
        name=overrides.get("name", "测试人员"),
        id_card=overrides.get("id_card", "encrypted-id-card"),
        phone=overrides.get("phone", "13800000001"),
        email=overrides.get("email", "test@company.com"),
        skill_tags=overrides.get("skill_tags", '["Java","Python"]'),
        level=overrides.get("level", 3),
        daily_rate=overrides.get("daily_rate", Decimal("1200.00")),
        department=overrides.get("department", "研发组"),
        pool_status=overrides.get("pool_status", 0),
        current_project=overrides.get("current_project"),
        entry_date=overrides.get("entry_date", date(2026, 1, 15)),
        exit_date=overrides.get("exit_date"),
        background_check=overrides.get("background_check", 1),
        security_review=overrides.get("security_review", 1),
        confidentiality_agreement=overrides.get("confidentiality_agreement", 1),
        attendance_group=overrides.get("attendance_group", "总行考勤组A"),
    )


# ═══════════════════════════════════════════════════════════════════════
# F-501: Outsource Person Management
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_create_person(client, db_session):
    resp = await client.post("/api/resource/persons", json={
        "emp_code": "EMP-001",
        "name": "张三",
        "id_card": "encrypted-001",
        "phone": "13900000001",
        "email": "emp001@company.com",
        "skill_tags": ["Java", "Spring"],
        "level": 3,
        "daily_rate": 1500.00,
        "department": "开发组",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert "personId" in data["data"]


@pytest.mark.asyncio
async def test_get_persons_list(client, db_session):
    for i in range(3):
        db_session.add(_make_person(person_id=f"p-list-{i}", emp_code=f"LC-{i}"))
    await db_session.flush()

    resp = await client.get("/api/resource/persons", params={"page": 1, "size": 10})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "SUCCESS"
    assert data["data"]["total"] >= 3
    assert len(data["data"]["records"]) > 0
    rec = data["data"]["records"][0]
    assert "personId" in rec
    assert "name" in rec
    assert "level" in rec


@pytest.mark.asyncio
async def test_get_person_detail(client, db_session):
    db_session.add(_make_person(person_id="p-detail-1", emp_code="DT-001"))
    db_session.add(SkillProfile(
        skill_id="sk-1", person_id="p-detail-1", skill_name="Java", proficiency=3,
    ))
    await db_session.flush()

    resp = await client.get("/api/resource/person/p-detail-1")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["name"] == "测试人员"
    assert len(data["skills"]) == 1
    assert data["skills"][0]["skillName"] == "Java"


@pytest.mark.asyncio
async def test_update_person(client, db_session):
    db_session.add(_make_person(person_id="p-update-1", emp_code="UP-001"))
    await db_session.flush()

    resp = await client.put("/api/resource/person/p-update-1", json={
        "name": "更新人员",
        "level": 4,
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"

    resp = await client.get("/api/resource/person/p-update-1")
    data = resp.json()["data"]
    assert data["name"] == "更新人员"
    assert data["level"] == 4


@pytest.mark.asyncio
async def test_delete_person(client, db_session):
    db_session.add(_make_person(person_id="p-del-1", emp_code="DL-001", pool_status=0))
    await db_session.flush()

    resp = await client.delete("/api/resource/person/p-del-1")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"

    resp = await client.get("/api/resource/person/p-del-1")
    assert resp.json()["data"]["poolStatus"] == 2


@pytest.mark.asyncio
async def test_persons_filter_by_level(client, db_session):
    db_session.add(_make_person(person_id="p-l1", emp_code="FL-01", level=2))
    db_session.add(_make_person(person_id="p-l2", emp_code="FL-02", level=3))
    await db_session.flush()

    resp = await client.get("/api/resource/persons", params={"level": 3})
    data = resp.json()["data"]
    assert all(r["level"] == 3 for r in data["records"])


@pytest.mark.asyncio
async def test_persons_filter_by_keyword(client, db_session):
    db_session.add(_make_person(person_id="p-kw1", emp_code="KW-01", name="张三"))
    db_session.add(_make_person(person_id="p-kw2", emp_code="KW-02", name="李四"))
    await db_session.flush()

    resp = await client.get("/api/resource/persons", params={"keyword": "张三"})
    data = resp.json()["data"]
    assert all("张三" in r["name"] for r in data["records"])


@pytest.mark.asyncio
async def test_get_person_not_found(client):
    resp = await client.get("/api/resource/person/nonexistent-id")
    assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════
# F-502: Skill Profiles
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_create_skill(client, db_session):
    db_session.add(_make_person(person_id="p-skill-1", emp_code="SK-001"))
    await db_session.flush()

    resp = await client.post("/api/resource/skills", json={
        "person_id": "p-skill-1",
        "skill_name": "Vue.js",
        "proficiency": 2,
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["skillId"]


@pytest.mark.asyncio
async def test_list_skills(client, db_session):
    db_session.add(_make_person(person_id="p-lsk-1", emp_code="LSK-001"))
    db_session.add(SkillProfile(skill_id="lsk-1", person_id="p-lsk-1", skill_name="React", proficiency=3))
    db_session.add(SkillProfile(skill_id="lsk-2", person_id="p-lsk-1", skill_name="TypeScript", proficiency=2))
    await db_session.flush()

    resp = await client.get("/api/resource/skills/p-lsk-1")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


@pytest.mark.asyncio
async def test_search_skills(client, db_session):
    db_session.add(_make_person(person_id="p-srch-1", emp_code="SR-001"))
    db_session.add(SkillProfile(skill_id="sr-1", person_id="p-srch-1", skill_name="Java", proficiency=3))
    db_session.add(SkillProfile(skill_id="sr-2", person_id="p-srch-1", skill_name="Python", proficiency=2))
    await db_session.flush()

    resp = await client.get("/api/resource/skills/search", params={"q": "Java"})
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["skillName"] == "Java"


@pytest.mark.asyncio
async def test_update_skill(client, db_session):
    db_session.add(_make_person(person_id="p-usk-1", emp_code="USK-001"))
    db_session.add(SkillProfile(skill_id="us-1", person_id="p-usk-1", skill_name="Go", proficiency=1))
    await db_session.flush()

    resp = await client.put("/api/resource/skills/us-1", json={"proficiency": 3})
    assert resp.status_code == 200

    resp = await client.get("/api/resource/skills/p-usk-1")
    skills = resp.json()["data"]
    assert skills[0]["proficiency"] == 3


@pytest.mark.asyncio
async def test_delete_skill(client, db_session):
    db_session.add(_make_person(person_id="p-dsk-1", emp_code="DSK-001"))
    db_session.add(SkillProfile(skill_id="ds-1", person_id="p-dsk-1", skill_name="Rust", proficiency=2))
    await db_session.flush()

    resp = await client.delete("/api/resource/skills/ds-1")
    assert resp.status_code == 200

    resp = await client.get("/api/resource/skills/p-dsk-1")
    assert len(resp.json()["data"]) == 0


# ═══════════════════════════════════════════════════════════════════════
# F-503: Pool Positions
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_create_position(client, db_session):
    db_session.add(ResourcePool(pool_id="pool-pos-1", pool_name="测试池"))
    await db_session.flush()

    resp = await client.post("/api/resource/positions", json={
        "pool_id": "pool-pos-1",
        "position_name": "高级Java开发",
        "level": 3,
        "skill_requirements": ["Java", "Spring Boot"],
        "head_count": 5,
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["positionId"]


@pytest.mark.asyncio
async def test_list_positions(client, db_session):
    db_session.add(ResourcePool(pool_id="pool-lp-1", pool_name="岗位测试池"))
    db_session.add(PoolPosition(position_id="pos-1", pool_id="pool-lp-1", position_name="前端开发", level=2, head_count=3))
    await db_session.flush()

    resp = await client.get("/api/resource/positions")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_update_position(client, db_session):
    db_session.add(ResourcePool(pool_id="pool-up-1", pool_name="更新池"))
    db_session.add(PoolPosition(position_id="pos-up", pool_id="pool-up-1", position_name="旧名称", level=2, head_count=1))
    await db_session.flush()

    resp = await client.put("/api/resource/positions/pos-up", json={
        "position_name": "新名称",
        "head_count": 5,
    })
    assert resp.status_code == 200

    resp = await client.get("/api/resource/positions")
    pos = next(p for p in resp.json()["data"] if p["positionId"] == "pos-up")
    assert pos["positionName"] == "新名称"
    assert pos["headCount"] == 5


@pytest.mark.asyncio
async def test_delete_position(client, db_session):
    db_session.add(ResourcePool(pool_id="pool-del-pos", pool_name="删除池"))
    db_session.add(PoolPosition(position_id="pos-del", pool_id="pool-del-pos", position_name="临时岗", level=1))
    await db_session.flush()

    resp = await client.delete("/api/resource/positions/pos-del")
    assert resp.status_code == 200

    resp = await client.get("/api/resource/positions")
    assert not any(p["positionId"] == "pos-del" for p in resp.json()["data"])


# ═══════════════════════════════════════════════════════════════════════
# F-504 / F-511: Entry / Exit Pool
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_apply_entry(client, db_session):
    db_session.add(_make_person(person_id="p-entry-1", emp_code="EN-001"))
    db_session.add(ResourcePool(pool_id="pool-entry", pool_name="入池测试"))
    await db_session.flush()

    resp = await client.post("/api/resource/person/p-entry-1/entry", json={
        "pool_id": "pool-entry",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["membershipId"]


@pytest.mark.asyncio
async def test_approve_entry(client, db_session):
    db_session.add(_make_person(person_id="p-app-1", emp_code="AP-001"))
    db_session.add(PoolMembership(
        membership_id="mem-app", person_id="p-app-1", pool_id="pool-app",
        status=0,
    ))
    await db_session.flush()

    resp = await client.post("/api/resource/person/p-app-1/entry/approve", json={
        "approver_id": "admin-001",
    })
    assert resp.status_code == 200

    # Verify person status changed to 1
    resp = await client.get("/api/resource/person/p-app-1")
    assert resp.json()["data"]["poolStatus"] == 1


@pytest.mark.asyncio
async def test_apply_exit(client, db_session):
    db_session.add(_make_person(person_id="p-exit-1", emp_code="EX-001", pool_status=1))
    db_session.add(PoolMembership(
        membership_id="mem-exit", person_id="p-exit-1", pool_id="pool-exit",
        status=1,
    ))
    await db_session.flush()

    resp = await client.post("/api/resource/person/p-exit-1/exit", json={})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_exit_updates_person_status(client, db_session):
    db_session.add(_make_person(person_id="p-exit2-1", emp_code="EX2-001", pool_status=1))
    db_session.add(PoolMembership(
        membership_id="mem-exit2", person_id="p-exit2-1", pool_id="pool-exit2",
        status=1,
    ))
    await db_session.flush()

    await client.post("/api/resource/person/p-exit2-1/exit", json={})

    resp = await client.get("/api/resource/person/p-exit2-1")
    assert resp.json()["data"]["poolStatus"] == 0


@pytest.mark.asyncio
async def test_list_pending_entry_exit(client, db_session):
    db_session.add(PoolMembership(
        membership_id="mem-pending", person_id="p-pend-1", pool_id="pool-pend",
        status=0,
    ))
    await db_session.flush()

    resp = await client.get("/api/resource/entry-exit/pending")
    data = resp.json()["data"]
    assert data["total"] >= 1
    assert any(r["membershipId"] == "mem-pending" for r in data["records"])


@pytest.mark.asyncio
async def test_exit_without_active_membership(client, db_session):
    db_session.add(_make_person(person_id="p-noexit", emp_code="NE-001", pool_status=0))
    await db_session.flush()

    resp = await client.post("/api/resource/person/p-noexit/exit", json={})
    assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════
# F-505: Skill Matching
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_match_candidates_by_skills(client, db_session):
    db_session.add(_make_person(person_id="p-match-1", emp_code="MA-001", pool_status=0,
                                 skill_tags='["Java","Spring"]', level=3))
    db_session.add(_make_person(person_id="p-match-2", emp_code="MA-002", pool_status=0,
                                 skill_tags='["Python"]', level=2))
    await db_session.flush()

    resp = await client.post("/api/resource/match", json={
        "skill_requirements": ["Java"],
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) > 0
    # Java-skilled person should rank first
    assert data[0]["personId"] == "p-match-1"
    assert data[0]["skillMatch"] == 40


@pytest.mark.asyncio
async def test_match_no_results(client, db_session):
    resp = await client.post("/api/resource/match", json={
        "skill_requirements": ["COBOL", "Fortran"],
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert all(c["skillMatch"] == 0 for c in data)


# ═══════════════════════════════════════════════════════════════════════
# F-506: Attendance Records
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_attendance_checkin(client, db_session):
    db_session.add(_make_person(person_id="p-att-1", emp_code="AT-001"))
    await db_session.flush()

    resp = await client.post("/api/resource/attendance/checkin", json={
        "person_id": "p-att-1",
        "gps_lat": 39.9042,
        "gps_lng": 116.4074,
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
    assert "attendanceId" in resp.json()["data"]


@pytest.mark.asyncio
async def test_attendance_checkout(client, db_session):
    db_session.add(_make_person(person_id="p-co-1", emp_code="CO-001"))
    await db_session.flush()

    await client.post("/api/resource/attendance/checkin", json={"person_id": "p-co-1"})

    resp = await client.post("/api/resource/attendance/checkout", json={
        "person_id": "p-co-1",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_attendance_calendar(client, db_session):
    db_session.add(_make_person(person_id="p-cal-1", emp_code="CA-001"))
    await db_session.flush()

    await client.post("/api/resource/attendance/checkin", json={"person_id": "p-cal-1"})

    resp = await client.get("/api/resource/attendance/calendar/p-cal-1/2026-04")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) >= 1
    assert data[0]["status"] == 0


@pytest.mark.asyncio
async def test_attendance_exceptions(client, db_session):
    db_session.add(_make_person(person_id="p-exc-1", emp_code="EC-001"))
    db_session.add(AttendanceRecord(
        attendance_id="exc-1", person_id="p-exc-1", date=date(2026, 4, 1),
        status=1,  # 迟到
    ))
    await db_session.flush()

    resp = await client.get("/api/resource/attendance/exceptions")
    data = resp.json()["data"]
    assert data["total"] >= 1


# ═══════════════════════════════════════════════════════════════════════
# F-508 / F-509: Settlement
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_list_settlements(client, db_session):
    db_session.add(_make_person(person_id="p-ls-1", emp_code="LS-001"))
    db_session.add(Settlement(
        settlement_id="set-ls-1", person_id="p-ls-1", period="2026-04",
        valid_hours=Decimal("160"), standard_hours=Decimal("176"),
        daily_rate=Decimal("1200"), performance_coeff=Decimal("1.0"),
        total_amount=Decimal("24000"), status=0,
    ))
    await db_session.flush()

    resp = await client.get("/api/resource/settlements", params={"page": 1, "size": 10})
    data = resp.json()["data"]
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_confirm_settlement(client, db_session):
    db_session.add(_make_person(person_id="p-conf-1", emp_code="CF-001"))
    db_session.add(Settlement(
        settlement_id="set-conf", person_id="p-conf-1", period="2026-04",
        status=0,
    ))
    await db_session.flush()

    resp = await client.put("/api/resource/settlement/set-conf/confirm", json={
        "confirmed_by": "admin-001",
    })
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


@pytest.mark.asyncio
async def test_reject_settlement(client, db_session):
    db_session.add(_make_person(person_id="p-rej-1", emp_code="RJ-001"))
    db_session.add(Settlement(
        settlement_id="set-rej", person_id="p-rej-1", period="2026-04",
        status=1,
    ))
    await db_session.flush()

    resp = await client.put("/api/resource/settlement/set-rej/reject")
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════
# F-510: Performance Evaluation
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_evaluate_person(client, db_session):
    db_session.add(_make_person(person_id="p-eval-1", emp_code="EV-001"))
    await db_session.flush()

    resp = await client.post("/api/resource/performance/evaluate/p-eval-1/2026-Q1", json={
        "pm_satisfaction": 90,
        "timesheet_compliance": 85,
        "task_completion": 88,
        "quality_metric": 92,
        "attendance_compliance": 95,
        "evaluator_id": "admin-001",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "evalId" in data
    assert "overallScore" in data
    assert "grade" in data


@pytest.mark.asyncio
async def test_grade_computation(client, db_session):
    db_session.add(_make_person(person_id="p-grade-1", emp_code="GR-001"))
    await db_session.flush()

    # Score 92 overall -> Grade A
    resp = await client.post("/api/resource/performance/evaluate/p-grade-1/2026-Q2", json={
        "pm_satisfaction": 95,
        "timesheet_compliance": 90,
        "task_completion": 92,
        "quality_metric": 90,
        "attendance_compliance": 88,
        "evaluator_id": "admin-001",
    })
    data = resp.json()["data"]
    overall = data["overallScore"]
    grade = data["grade"]
    assert grade == "A"
    assert overall >= 90

    # Score 70 overall -> Grade C
    resp = await client.post("/api/resource/performance/evaluate/p-grade-1/2026-Q3", json={
        "pm_satisfaction": 65,
        "timesheet_compliance": 70,
        "task_completion": 75,
        "quality_metric": 72,
        "attendance_compliance": 68,
        "evaluator_id": "admin-001",
    })
    data = resp.json()["data"]
    assert data["grade"] == "C"


@pytest.mark.asyncio
async def test_update_evaluation(client, db_session):
    db_session.add(_make_person(person_id="p-upd-1", emp_code="UE-001"))
    await db_session.flush()

    # Create eval
    resp = await client.post("/api/resource/performance/evaluate/p-upd-1/2026-Q1", json={
        "pm_satisfaction": 80,
        "timesheet_compliance": 75,
        "task_completion": 70,
        "quality_metric": 78,
        "attendance_compliance": 82,
        "evaluator_id": "admin-001",
    })
    eval_id = resp.json()["data"]["evalId"]

    # Update
    resp = await client.put(f"/api/resource/performance/{eval_id}", json={
        "pm_satisfaction": 95,
    })
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_performance_history(client, db_session):
    db_session.add(_make_person(person_id="p-hist-1", emp_code="HI-001"))
    db_session.add(PerformanceEval(
        eval_id="eval-hist-1", person_id="p-hist-1", period="2026-Q1",
        pm_satisfaction=Decimal("85"), timesheet_compliance=Decimal("80"),
        task_completion=Decimal("82"), quality_metric=Decimal("88"),
        attendance_compliance=Decimal("90"), overall_score=Decimal("84.2"),
        grade="B",
    ))
    db_session.add(PerformanceEval(
        eval_id="eval-hist-2", person_id="p-hist-1", period="2026-Q2",
        pm_satisfaction=Decimal("90"), timesheet_compliance=Decimal("85"),
        task_completion=Decimal("88"), quality_metric=Decimal("92"),
        attendance_compliance=Decimal("95"), overall_score=Decimal("90.1"),
        grade="A",
    ))
    await db_session.flush()

    resp = await client.get("/api/resource/performance/p-hist-1/history",
                            params={"page": 1, "size": 10})
    data = resp.json()["data"]
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_list_performance(client, db_session):
    db_session.add(_make_person(person_id="p-lpe-1", emp_code="LPE-001"))
    db_session.add(PerformanceEval(
        eval_id="eval-lpe", person_id="p-lpe-1", period="2026-Q1",
        overall_score=Decimal("80"), grade="B",
    ))
    await db_session.flush()

    resp = await client.get("/api/resource/performance", params={"person_id": "p-lpe-1"})
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


@pytest.mark.asyncio
async def test_delete_evaluation(client, db_session):
    db_session.add(PerformanceEval(
        eval_id="eval-del", person_id="p-del-eval", period="2026-Q1",
        overall_score=Decimal("70"),
    ))
    await db_session.flush()

    resp = await client.delete("/api/resource/performance/eval-del")
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════
# F-512: Utilization Analysis
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_utilization_person(client, db_session):
    db_session.add(_make_person(person_id="p-util-1", emp_code="UT-001"))
    await db_session.flush()

    resp = await client.get("/api/resource/utilization/person/p-util-1")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "personId" in data
    assert "totalHours" in data
    assert "loadRate" in data
    assert "status" in data


@pytest.mark.asyncio
async def test_utilization_warnings(client, db_session):
    db_session.add(_make_person(person_id="p-warn-1", emp_code="WR-001"))
    await db_session.flush()

    resp = await client.get("/api/resource/utilization/warnings")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


# ═══════════════════════════════════════════════════════════════════════
# F-513: Efficiency Reports
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_efficiency_report(client, db_session):
    db_session.add(_make_person(person_id="p-eff-1", emp_code="EF-001", pool_status=0))
    await db_session.flush()

    resp = await client.get("/api/resource/reports/efficiency")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"


# ═══════════════════════════════════════════════════════════════════════
# Full Lifecycle Tests
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_full_lifecycle(client, db_session):
    """Create -> Entry -> Checkin -> Checkout -> Settlement -> Performance."""
    # 1. Create person
    resp = await client.post("/api/resource/persons", json={
        "emp_code": "LIFE-001",
        "name": "生命周期测试",
        "id_card": "encrypted-life",
        "skill_tags": ["Java"],
        "level": 3,
        "daily_rate": 1200.00,
        "department": "测试组",
    })
    person_id = resp.json()["data"]["personId"]

    # 2. Entry pool
    db_session.add(ResourcePool(pool_id="pool-life", pool_name="生命周期池"))
    await db_session.flush()
    resp = await client.post(f"/api/resource/person/{person_id}/entry", json={
        "pool_id": "pool-life",
    })
    membership_id = resp.json()["data"]["membershipId"]

    # 3. Approve entry
    resp = await client.post(f"/api/resource/person/{person_id}/entry/approve", json={
        "approver_id": "admin-001",
    })
    assert resp.status_code == 200

    # 4. Verify status is now "在池" (1)
    resp = await client.get(f"/api/resource/person/{person_id}")
    assert resp.json()["data"]["poolStatus"] == 1

    # 5. Attendance checkin
    resp = await client.post("/api/resource/attendance/checkin", json={
        "person_id": person_id,
    })
    assert resp.status_code == 200

    # 6. Attendance checkout
    resp = await client.post("/api/resource/attendance/checkout", json={
        "person_id": person_id,
    })
    assert resp.status_code == 200

    # 7. Performance evaluation
    resp = await client.post(f"/api/resource/performance/evaluate/{person_id}/2026-Q1", json={
        "pm_satisfaction": 88,
        "timesheet_compliance": 85,
        "task_completion": 90,
        "quality_metric": 82,
        "attendance_compliance": 95,
        "evaluator_id": "admin-001",
    })
    assert resp.status_code == 200
    assert resp.json()["data"]["grade"] in ("A", "B", "C", "D")


@pytest.mark.asyncio
async def test_entry_exit_lifecycle(client, db_session):
    """Entry -> Approve -> Exit -> Re-entry."""
    db_session.add(_make_person(person_id="p-cycle-1", emp_code="CY-001", pool_status=0))
    db_session.add(ResourcePool(pool_id="pool-cycle", pool_name="周期池"))
    await db_session.flush()

    # Entry
    resp = await client.post("/api/resource/person/p-cycle-1/entry", json={
        "pool_id": "pool-cycle",
    })
    assert resp.status_code == 200

    # Approve
    resp = await client.post("/api/resource/person/p-cycle-1/entry/approve", json={
        "approver_id": "admin-001",
    })
    assert resp.status_code == 200

    # Verify in pool
    resp = await client.get("/api/resource/person/p-cycle-1")
    assert resp.json()["data"]["poolStatus"] == 1

    # Exit
    resp = await client.post("/api/resource/person/p-cycle-1/exit", json={})
    assert resp.status_code == 200

    # Verify exited
    resp = await client.get("/api/resource/person/p-cycle-1")
    assert resp.json()["data"]["poolStatus"] == 0


# ═══════════════════════════════════════════════════════════════════════
# Edge Cases & Validation
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_create_person_missing_required_fields(client):
    resp = await client.post("/api/resource/persons", json={
        "emp_code": "MISS-001",
    })
    assert resp.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_person_duplicate_emp_code(client, db_session):
    db_session.add(_make_person(person_id="p-dup-1", emp_code="DUP-001"))
    await db_session.flush()

    resp = await client.post("/api/resource/persons", json={
        "emp_code": "DUP-001",
        "name": "重复工号",
        "id_card": "encrypted-dup",
        "level": 2,
        "daily_rate": 1000.00,
    })
    assert resp.status_code == 422  # Unique constraint violation


@pytest.mark.asyncio
async def test_invalid_person_id_returns_404(client):
    resp = await client.get("/api/resource/person/invalid-uuid")
    assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════
# Legacy: Pool CRUD, Leave, Replacement
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_pool_crud(client, db_session):
    # Create
    resp = await client.post("/api/resource/pools", json={
        "pool_name": "测试资源池",
        "manager_id": "admin-001",
        "description": "测试用途",
    })
    assert resp.status_code == 200
    pool_id = resp.json()["data"]["poolId"]

    # List
    resp = await client.get("/api/resource/pools")
    assert resp.status_code == 200
    assert any(p["poolId"] == pool_id for p in resp.json()["data"])


@pytest.mark.asyncio
async def test_leave_request_crud(client, db_session):
    db_session.add(_make_person(person_id="p-leave-1", emp_code="LV-001"))
    await db_session.flush()

    # Create leave request
    resp = await client.post("/api/resource/leave", json={
        "person_id": "p-leave-1",
        "leave_type": "年假",
        "start_date": "2026-05-01",
        "end_date": "2026-05-03",
        "days": 3,
        "reason": "个人事务",
    })
    assert resp.status_code == 200
    leave_id = resp.json()["data"]["leaveId"]

    # List
    resp = await client.get("/api/resource/leave", params={"person_id": "p-leave-1"})
    data = resp.json()["data"]
    assert data["total"] >= 1

    # Approve
    resp = await client.post(f"/api/resource/leave/{leave_id}/approve")
    assert resp.status_code == 200
    assert resp.json()["code"] == "SUCCESS"
