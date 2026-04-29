"""Resource pool management API — F-501 to F-513.

Covers: OutsourcePerson (F-501), SkillProfile (F-502), PoolPosition (F-503),
PoolMembership entry/exit (F-504/F-511), Skill matching (F-505),
Attendance (F-506), Timesheet helpers (F-507), Settlement (F-508/F-509),
Performance 5-dimension (F-510), Utilization (F-512), Reports (F-513).
"""

from __future__ import annotations

import json
import uuid
from typing import Optional

from datetime import date as date_type, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ApiResponse, PageResult
from app.database import get_db
from app.exceptions import ResourceNotFoundError, ValidationError
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

router = APIRouter(tags=["resource"])


# ── helpers ───────────────────────────────────────────────────────────

def _person_to_dict(p: OutsourcePerson) -> dict:
    skill_list = []
    try:
        skill_list = json.loads(p.skill_tags) if p.skill_tags else []
    except (json.JSONDecodeError, TypeError):
        pass
    data = {
        "personId": p.person_id, "empCode": p.emp_code, "name": p.name,
        "phone": p.phone, "email": p.email, "skillTags": skill_list,
        "level": p.level, "dailyRate": float(p.daily_rate) if p.daily_rate else None,
        "department": p.department, "poolStatus": p.pool_status,
        "currentProject": p.current_project,
        "entryDate": str(p.entry_date) if p.entry_date else None,
        "exitDate": str(p.exit_date) if p.exit_date else None,
        "backgroundCheck": p.background_check,
        "securityReview": p.security_review,
        "confidentialityAgreement": p.confidentiality_agreement,
        "attendanceGroup": p.attendance_group,
    }
    data.update(p.decrypt_fields())
    return data


def _eval_to_dict(e: PerformanceEval) -> dict:
    return {
        "evalId": e.eval_id, "personId": e.person_id,
        "projectId": e.project_id, "period": e.period,
        "pmSatisfaction": float(e.pm_satisfaction) if e.pm_satisfaction else None,
        "timesheetCompliance": float(e.timesheet_compliance) if e.timesheet_compliance else None,
        "taskCompletion": float(e.task_completion) if e.task_completion else None,
        "qualityMetric": float(e.quality_metric) if e.quality_metric else None,
        "attendanceCompliance": float(e.attendance_compliance) if e.attendance_compliance else None,
        "overallScore": float(e.overall_score) if e.overall_score else None,
        "grade": e.grade, "evaluatorId": e.evaluator_id, "comments": e.comments,
    }


def _compute_grade(overall: float) -> str:
    if overall >= 90:
        return "A"
    if overall >= 75:
        return "B"
    if overall >= 60:
        return "C"
    return "D"


# ═══════════════════════════════════════════════════════════════════════
# F-501: Outsource Person Management
# ═══════════════════════════════════════════════════════════════════════

@router.get("/persons")
async def list_persons(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    keyword: str | None = None, level: int | None = None,
    pool_status: int | None = None, department: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(OutsourcePerson).order_by(OutsourcePerson.create_time.desc())
    if keyword:
        stmt = stmt.where(
            OutsourcePerson.name.like(f"%{keyword}%")
            | OutsourcePerson.emp_code.like(f"%{keyword}%")
        )
    if level is not None:
        stmt = stmt.where(OutsourcePerson.level == level)
    if pool_status is not None:
        stmt = stmt.where(OutsourcePerson.pool_status == pool_status)
    if department:
        stmt = stmt.where(OutsourcePerson.department == department)

    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[_person_to_dict(p) for p in items],
    ))


@router.get("/person/{person_id}")
async def get_person(person_id: str, db: AsyncSession = Depends(get_db)):
    p = await db.get(OutsourcePerson, person_id)
    if not p:
        raise ResourceNotFoundError("OutsourcePerson", person_id)
    skills_stmt = select(SkillProfile).where(SkillProfile.person_id == person_id)
    skills_result = await db.execute(skills_stmt)
    skills = skills_result.scalars().all()
    data = _person_to_dict(p)
    data["skills"] = [
        {"skillId": s.skill_id, "skillName": s.skill_name,
         "proficiency": s.proficiency, "certName": s.cert_name,
         "certDate": str(s.cert_date) if s.cert_date else None}
        for s in skills
    ]
    return ApiResponse(code="SUCCESS", message="success", data=data)


@router.post("/persons")
async def create_person(req: PersonCreateRequest, db: AsyncSession = Depends(get_db)):
    p = OutsourcePerson(
        person_id=str(uuid.uuid4()), emp_code=req.emp_code, name=req.name,
        id_card=req.id_card, phone=req.phone, email=req.email,
        skill_tags=json.dumps(req.skill_tags, ensure_ascii=False) if req.skill_tags else None,
        level=req.level, daily_rate=req.daily_rate, department=req.department,
        pool_status=req.pool_status or 0, current_project=req.current_project,
        entry_date=req.entry_date,
        background_check=req.background_check or 0,
        security_review=req.security_review or 0,
        confidentiality_agreement=req.confidentiality_agreement or 0,
        attendance_group=req.attendance_group,
    )
    p.encrypt_fields()
    db.add(p)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise ValidationError(message=f"emp_code '{req.emp_code}' already exists", field="emp_code")
    return ApiResponse(code="SUCCESS", message="success", data={"personId": p.person_id})


@router.put("/person/{person_id}")
async def update_person(person_id: str, req: PersonUpdateRequest, db: AsyncSession = Depends(get_db)):
    p = await db.get(OutsourcePerson, person_id)
    if not p:
        raise ResourceNotFoundError("OutsourcePerson", person_id)
    for field in req.model_fields_set:
        value = getattr(req, field)
        if field == "skill_tags" and value is not None:
            value = json.dumps(value, ensure_ascii=False)
        setattr(p, field, value)
    p.encrypt_fields()
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"personId": p.person_id})


@router.delete("/person/{person_id}")
async def delete_person(person_id: str, db: AsyncSession = Depends(get_db)):
    p = await db.get(OutsourcePerson, person_id)
    if not p:
        raise ResourceNotFoundError("OutsourcePerson", person_id)
    p.pool_status = 2
    p.exit_date = date_type.today()
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ═══════════════════════════════════════════════════════════════════════
# F-502: Skill Profiles
# ═══════════════════════════════════════════════════════════════════════

# NOTE: Static routes MUST come before dynamic routes with path params
@router.get("/skills/search")
async def search_skills(q: str = Query(...), db: AsyncSession = Depends(get_db)):
    stmt = select(SkillProfile).where(SkillProfile.skill_name.like(f"%{q}%"))
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"skillId": s.skill_id, "personId": s.person_id,
         "skillName": s.skill_name, "proficiency": s.proficiency}
        for s in items
    ])


@router.get("/skills/{person_id}")
async def list_skills(person_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(SkillProfile).where(SkillProfile.person_id == person_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"skillId": s.skill_id, "skillName": s.skill_name,
         "proficiency": s.proficiency, "certName": s.cert_name,
         "certDate": str(s.cert_date) if s.cert_date else None,
         "expiryDate": str(s.expiry_date) if s.expiry_date else None}
        for s in items
    ])


@router.post("/skills")
async def create_skill(req: SkillCreateRequest, db: AsyncSession = Depends(get_db)):
    s = SkillProfile(
        skill_id=str(uuid.uuid4()), person_id=req.person_id,
        skill_name=req.skill_name, proficiency=req.proficiency,
        cert_name=req.cert_name, cert_date=req.cert_date,
        expiry_date=req.expiry_date,
    )
    db.add(s)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"skillId": s.skill_id})


@router.put("/skills/{skill_id}")
async def update_skill(skill_id: str, req: SkillUpdateRequest, db: AsyncSession = Depends(get_db)):
    s = await db.get(SkillProfile, skill_id)
    if not s:
        raise ResourceNotFoundError("SkillProfile", skill_id)
    for field in req.model_fields_set:
        setattr(s, field, getattr(req, field))
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/skills/{skill_id}")
async def delete_skill(skill_id: str, db: AsyncSession = Depends(get_db)):
    s = await db.get(SkillProfile, skill_id)
    if not s:
        raise ResourceNotFoundError("SkillProfile", skill_id)
    await db.delete(s)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ═══════════════════════════════════════════════════════════════════════
# F-503: Pool Positions
# ═══════════════════════════════════════════════════════════════════════

@router.get("/positions")
async def list_positions(pool_id: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(PoolPosition)
    if pool_id:
        stmt = stmt.where(PoolPosition.pool_id == pool_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"positionId": p.position_id, "poolId": p.pool_id,
         "positionName": p.position_name, "level": p.level,
         "skillRequirements": p.skill_requirements,
         "headCount": p.head_count, "filledCount": p.filled_count,
         "department": p.department, "status": p.status}
        for p in items
    ])


@router.post("/positions")
async def create_position(req: PositionCreateRequest, db: AsyncSession = Depends(get_db)):
    p = PoolPosition(
        position_id=str(uuid.uuid4()), pool_id=req.pool_id,
        position_name=req.position_name, level=req.level,
        skill_requirements=json.dumps(req.skill_requirements, ensure_ascii=False) if req.skill_requirements else None,
        head_count=req.head_count or 1, filled_count=0,
        department=req.department, status=req.status or 1,
    )
    db.add(p)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"positionId": p.position_id})


@router.put("/positions/{position_id}")
async def update_position(position_id: str, req: PositionUpdateRequest, db: AsyncSession = Depends(get_db)):
    p = await db.get(PoolPosition, position_id)
    if not p:
        raise ResourceNotFoundError("PoolPosition", position_id)
    for field in req.model_fields_set:
        value = getattr(req, field)
        if field == "skill_requirements" and value is not None:
            value = json.dumps(value, ensure_ascii=False)
        setattr(p, field, value)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/positions/{position_id}")
async def delete_position(position_id: str, db: AsyncSession = Depends(get_db)):
    p = await db.get(PoolPosition, position_id)
    if not p:
        raise ResourceNotFoundError("PoolPosition", position_id)
    await db.delete(p)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ═══════════════════════════════════════════════════════════════════════
# F-504 / F-511: Entry / Exit Pool Management
# ═══════════════════════════════════════════════════════════════════════

@router.post("/person/{person_id}/entry")
async def apply_entry(person_id: str, req: EntryExitRequest, db: AsyncSession = Depends(get_db)):
    p = await db.get(OutsourcePerson, person_id)
    if not p:
        raise ResourceNotFoundError("OutsourcePerson", person_id)
    membership = PoolMembership(
        membership_id=str(uuid.uuid4()), person_id=person_id,
        pool_id=req.pool_id, status=0,
    )
    db.add(membership)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"membershipId": membership.membership_id})


@router.post("/person/{person_id}/entry/approve")
async def approve_entry(person_id: str, req: ApproveRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(PoolMembership).where(
        PoolMembership.person_id == person_id, PoolMembership.status == 0,
    ).order_by(PoolMembership.create_time.desc()).limit(1)
    result = await db.execute(stmt)
    m = result.scalar_one_or_none()
    if not m:
        raise ResourceNotFoundError("PoolMembership pending entry", person_id)

    m.status = 1
    m.entry_date = req.date or date_type.today()
    m.approved_by = req.approver_id
    m.approval_date = datetime.now()

    p = await db.get(OutsourcePerson, person_id)
    if p:
        p.pool_status = 1
        p.entry_date = m.entry_date
        p.attendance_group = req.attendance_group

    await db.flush()
    return ApiResponse(code="SUCCESS", message="入池审批通过")


@router.post("/person/{person_id}/exit")
async def apply_exit(person_id: str, req: ExitRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(PoolMembership).where(
        PoolMembership.person_id == person_id, PoolMembership.status == 1,
    ).order_by(PoolMembership.create_time.desc()).limit(1)
    result = await db.execute(stmt)
    m = result.scalar_one_or_none()
    if not m:
        raise ResourceNotFoundError("PoolMembership active", person_id)

    m.status = 2
    m.exit_date = req.exit_date or date_type.today()
    m.approved_by = req.approved_by

    p = await db.get(OutsourcePerson, person_id)
    if p:
        p.pool_status = 0
        p.exit_date = m.exit_date

    await db.flush()
    return ApiResponse(code="SUCCESS", message="人员已出池")


@router.get("/entry-exit/pending")
async def list_pending_entry_exit(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(PoolMembership).where(PoolMembership.status == 0)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{
            "membershipId": m.membership_id, "personId": m.person_id,
            "poolId": m.pool_id, "status": m.status,
            "entryDate": str(m.entry_date) if m.entry_date else None,
        } for m in items],
    ))


# ═══════════════════════════════════════════════════════════════════════
# F-505: Skill Matching
# ═══════════════════════════════════════════════════════════════════════

@router.post("/match")
async def match_candidates(req: MatchRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(OutsourcePerson).where(OutsourcePerson.pool_status.in_([0, 1]))
    result = await db.execute(stmt)
    persons = result.scalars().all()

    required_skills = req.skill_requirements or []
    candidates = []

    for p in persons:
        person_skills = []
        try:
            person_skills = json.loads(p.skill_tags) if p.skill_tags else []
        except (json.JSONDecodeError, TypeError):
            pass

        skill_match = 0
        for rs in required_skills:
            if rs in person_skills:
                skill_match += 40
        skill_match = min(skill_match, 40)

        exp_match = 20 if p.level >= (req.experience_min or 1) else 0

        perf_match = 0
        perf_stmt = select(PerformanceEval).where(
            PerformanceEval.person_id == p.person_id
        ).order_by(PerformanceEval.create_time.desc()).limit(1)
        perf_result = await db.execute(perf_stmt)
        latest_eval = perf_result.scalar_one_or_none()
        if latest_eval and latest_eval.overall_score:
            overall = float(latest_eval.overall_score)
            if overall >= 85:
                perf_match = 30
            elif overall >= 70:
                perf_match = 20

        idle_match = 10 if p.pool_status == 0 else 0
        score = skill_match + exp_match + perf_match + idle_match

        candidates.append({
            "personId": p.person_id, "name": p.name,
            "level": p.level, "department": p.department,
            "skillTags": person_skills,
            "score": score, "skillMatch": skill_match,
            "expMatch": exp_match, "perfMatch": perf_match, "idleMatch": idle_match,
        })

    candidates.sort(key=lambda c: c["score"], reverse=True)
    return ApiResponse(code="SUCCESS", message="success", data=candidates[:20])


# ═══════════════════════════════════════════════════════════════════════
# F-506: Attendance Records
# ═══════════════════════════════════════════════════════════════════════

@router.post("/attendance/checkin")
async def checkin(req: AttendanceCheckRequest, db: AsyncSession = Depends(get_db)):
    rec = AttendanceRecord(
        attendance_id=str(uuid.uuid4()), person_id=req.person_id,
        date=req.date or date_type.today(),
        check_in_time=datetime.now(),
        gps_lat=req.gps_lat, gps_lng=req.gps_lng,
        wifi_mac=req.wifi_mac, project_id=req.project_id,
        status=0,
    )
    db.add(rec)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="打卡成功", data={"attendanceId": rec.attendance_id})


@router.post("/attendance/checkout")
async def checkout(req: AttendanceCheckRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(AttendanceRecord).where(
        AttendanceRecord.person_id == req.person_id,
        AttendanceRecord.date == (req.date or date_type.today()),
    )
    result = await db.execute(stmt)
    rec = result.scalar_one_or_none()
    if not rec:
        raise ResourceNotFoundError("AttendanceRecord", req.person_id)
    rec.check_out_time = datetime.now()
    await db.flush()
    return ApiResponse(code="SUCCESS", message="签退成功")


@router.get("/attendance/calendar/{person_id}/{month}")
async def attendance_calendar(person_id: str, month: str, db: AsyncSession = Depends(get_db)):
    stmt = select(AttendanceRecord).where(
        AttendanceRecord.person_id == person_id,
        func.strftime("%Y-%m", AttendanceRecord.date) == month,
    ).order_by(AttendanceRecord.date)
    result = await db.execute(stmt)
    items = result.scalars().all()
    status_map = {0: "正常", 1: "迟到", 2: "早退", 3: "缺勤", 4: "外勤"}
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"date": str(r.date), "checkIn": str(r.check_in_time) if r.check_in_time else None,
         "checkOut": str(r.check_out_time) if r.check_out_time else None,
         "status": r.status, "statusText": status_map.get(r.status, "未知")}
        for r in items
    ])


@router.get("/attendance/exceptions")
async def attendance_exceptions(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(AttendanceRecord).where(AttendanceRecord.status.in_([1, 2, 3, 4]))
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    status_map = {1: "迟到", 2: "早退", 3: "缺勤", 4: "外勤"}
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{
            "attendanceId": r.attendance_id, "personId": r.person_id,
            "date": str(r.date), "status": r.status,
            "statusText": status_map.get(r.status, ""),
        } for r in items],
    ))


# ═══════════════════════════════════════════════════════════════════════
# F-508 / F-509: Monthly Settlement
# ═══════════════════════════════════════════════════════════════════════

@router.post("/settlement/generate/{period}")
async def generate_settlement(period: str, db: AsyncSession = Depends(get_db)):
    from app.models.timesheet.models import Timesheet

    stmt = select(Timesheet.staff_id, func.sum(Timesheet.hours).label("total_hours")).where(
        func.strftime("%Y-%m", Timesheet.work_date) == period,
        Timesheet.check_status == "approved",
    ).group_by(Timesheet.staff_id)
    result = await db.execute(stmt)
    rows = result.all()

    generated = 0
    for staff_id, total_hours in rows:
        p = await db.get(OutsourcePerson, staff_id)
        if not p or not p.daily_rate:
            continue

        perf_stmt = select(PerformanceEval).where(
            PerformanceEval.person_id == staff_id
        ).order_by(PerformanceEval.create_time.desc()).limit(1)
        perf_result = await db.execute(perf_stmt)
        latest_eval = perf_result.scalar_one_or_none()
        perf_coeff = Decimal("1.0")
        if latest_eval and latest_eval.overall_score:
            overall = float(latest_eval.overall_score)
            if overall >= 90:
                perf_coeff = Decimal("1.2")
            elif overall >= 75:
                perf_coeff = Decimal("1.0")
            elif overall >= 60:
                perf_coeff = Decimal("0.9")
            else:
                perf_coeff = Decimal("0.8")

        valid_hours = Decimal(str(total_hours))
        standard_hours = Decimal("176")
        amount = (valid_hours / Decimal("8")) * p.daily_rate * perf_coeff

        settlement = Settlement(
            settlement_id=str(uuid.uuid4()), person_id=staff_id,
            period=period, valid_hours=valid_hours,
            standard_hours=standard_hours, daily_rate=p.daily_rate,
            performance_coeff=perf_coeff, total_amount=amount,
            status=0,
        )
        db.add(settlement)
        generated += 1

    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"generated": generated})


@router.get("/settlements")
async def list_settlements(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    period: str | None = None, status: int | None = None,
    person_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Settlement).order_by(Settlement.create_time.desc())
    if period:
        stmt = stmt.where(Settlement.period == period)
    if status is not None:
        stmt = stmt.where(Settlement.status == status)
    if person_id:
        stmt = stmt.where(Settlement.person_id == person_id)

    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    status_map = {0: "草稿", 1: "待确认", 2: "已确认", 3: "已开票"}
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{
            "settlementId": s.settlement_id, "personId": s.person_id,
            "period": s.period,
            "validHours": float(s.valid_hours) if s.valid_hours else None,
            "dailyRate": float(s.daily_rate) if s.daily_rate else None,
            "performanceCoeff": float(s.performance_coeff) if s.performance_coeff else None,
            "totalAmount": float(s.total_amount) if s.total_amount else None,
            "status": s.status, "statusText": status_map.get(s.status, ""),
            "confirmedBy": s.confirmed_by,
            "confirmedDate": str(s.confirmed_date) if s.confirmed_date else None,
        } for s in items],
    ))


@router.get("/settlement/{settlement_id}")
async def get_settlement(settlement_id: str, db: AsyncSession = Depends(get_db)):
    s = await db.get(Settlement, settlement_id)
    if not s:
        raise ResourceNotFoundError("Settlement", settlement_id)
    p = await db.get(OutsourcePerson, s.person_id)
    return ApiResponse(code="SUCCESS", message="success", data={
        "settlementId": s.settlement_id, "personId": s.person_id,
        "personName": p.name if p else "", "period": s.period,
        "validHours": float(s.valid_hours) if s.valid_hours else None,
        "standardHours": float(s.standard_hours) if s.standard_hours else None,
        "dailyRate": float(s.daily_rate) if s.daily_rate else None,
        "performanceCoeff": float(s.performance_coeff) if s.performance_coeff else None,
        "overtimeHours": float(s.overtime_hours) if s.overtime_hours else None,
        "overtimeFee": float(s.overtime_fee) if s.overtime_fee else None,
        "totalAmount": float(s.total_amount) if s.total_amount else None,
        "status": s.status, "confirmedBy": s.confirmed_by,
    })


@router.put("/settlement/{settlement_id}/confirm")
async def confirm_settlement(settlement_id: str, req: ConfirmRequest, db: AsyncSession = Depends(get_db)):
    s = await db.get(Settlement, settlement_id)
    if not s:
        raise ResourceNotFoundError("Settlement", settlement_id)
    s.status = 2
    s.confirmed_by = req.confirmed_by
    s.confirmed_date = datetime.now()
    await db.flush()
    return ApiResponse(code="SUCCESS", message="结算已确认")


@router.put("/settlement/{settlement_id}/reject")
async def reject_settlement(settlement_id: str, db: AsyncSession = Depends(get_db)):
    s = await db.get(Settlement, settlement_id)
    if not s:
        raise ResourceNotFoundError("Settlement", settlement_id)
    s.status = 0
    await db.flush()
    return ApiResponse(code="SUCCESS", message="结算已驳回")


@router.post("/settlement/{settlement_id}/invoice")
async def invoice_settlement(settlement_id: str, db: AsyncSession = Depends(get_db)):
    s = await db.get(Settlement, settlement_id)
    if not s:
        raise ResourceNotFoundError("Settlement", settlement_id)
    if s.status != 2:
        raise ResourceNotFoundError("Settlement not confirmed", settlement_id)
    s.status = 3
    s.invoice_date = date_type.today()
    await db.flush()
    return ApiResponse(code="SUCCESS", message="开票申请已提交")


# ═══════════════════════════════════════════════════════════════════════
# F-510: Performance Evaluation (5-dimension)
# ═══════════════════════════════════════════════════════════════════════

@router.get("/performance")
async def list_performance(
    person_id: str | None = None, period: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(PerformanceEval)
    if person_id:
        stmt = stmt.where(PerformanceEval.person_id == person_id)
    if period:
        stmt = stmt.where(PerformanceEval.period == period)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[_eval_to_dict(e) for e in items])


@router.post("/performance/evaluate/{person_id}/{period}")
async def evaluate_performance(
    person_id: str, period: str,
    req: PerformanceEvaluateRequest, db: AsyncSession = Depends(get_db),
):
    overall = (
        req.pm_satisfaction * Decimal("0.4")
        + req.timesheet_compliance * Decimal("0.2")
        + req.task_completion * Decimal("0.2")
        + req.quality_metric * Decimal("0.1")
        + req.attendance_compliance * Decimal("0.1")
    )
    grade = _compute_grade(float(overall))

    pe = PerformanceEval(
        eval_id=str(uuid.uuid4()), person_id=person_id,
        project_id=req.project_id, period=period,
        pm_satisfaction=req.pm_satisfaction,
        timesheet_compliance=req.timesheet_compliance,
        task_completion=req.task_completion,
        quality_metric=req.quality_metric,
        attendance_compliance=req.attendance_compliance,
        overall_score=overall, grade=grade,
        evaluator_id=req.evaluator_id, comments=req.comments,
    )
    db.add(pe)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={
        "evalId": pe.eval_id, "overallScore": float(overall), "grade": grade,
    })


@router.put("/performance/{eval_id}")
async def update_performance(eval_id: str, req: PerformanceUpdateRequest, db: AsyncSession = Depends(get_db)):
    e = await db.get(PerformanceEval, eval_id)
    if not e:
        raise ResourceNotFoundError("PerformanceEval", eval_id)
    for field in req.model_fields_set:
        setattr(e, field, getattr(req, field))

    # Recompute overall and grade
    if all([e.pm_satisfaction, e.timesheet_compliance, e.task_completion, e.quality_metric, e.attendance_compliance]):
        e.overall_score = (
            e.pm_satisfaction * Decimal("0.4")
            + e.timesheet_compliance * Decimal("0.2")
            + e.task_completion * Decimal("0.2")
            + e.quality_metric * Decimal("0.1")
            + e.attendance_compliance * Decimal("0.1")
        )
        e.grade = _compute_grade(float(e.overall_score))

    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/performance/{eval_id}")
async def delete_performance(eval_id: str, db: AsyncSession = Depends(get_db)):
    e = await db.get(PerformanceEval, eval_id)
    if not e:
        raise ResourceNotFoundError("PerformanceEval", eval_id)
    await db.delete(e)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.get("/performance/{person_id}/history")
async def performance_history(
    person_id: str,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(PerformanceEval).where(
        PerformanceEval.person_id == person_id
    ).order_by(PerformanceEval.create_time.desc())
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[_eval_to_dict(e) for e in items],
    ))


# ═══════════════════════════════════════════════════════════════════════
# F-512: Utilization Analysis
# ═══════════════════════════════════════════════════════════════════════

@router.get("/utilization/person/{person_id}")
async def utilization_person(person_id: str, db: AsyncSession = Depends(get_db)):
    """Personal workload rate = (project hours + non-project hours) / available hours."""
    from app.models.timesheet.models import Timesheet

    stmt = select(func.sum(Timesheet.hours)).where(
        Timesheet.staff_id == person_id,
        Timesheet.check_status == "approved",
    )
    result = await db.execute(stmt)
    total_hours = result.scalar() or 0

    available_hours = Decimal("176")  # 22 workdays * 8h
    load_rate = float((Decimal(str(total_hours)) / available_hours) * 100) if available_hours else 0

    if 70 <= load_rate <= 85:
        status = "green"
    elif 85 < load_rate <= 100:
        status = "yellow"
    else:
        status = "red"

    return ApiResponse(code="SUCCESS", message="success", data={
        "personId": person_id, "totalHours": float(total_hours),
        "availableHours": float(available_hours),
        "loadRate": round(load_rate, 1), "status": status,
    })


@router.get("/utilization/warnings")
async def utilization_warnings(db: AsyncSession = Depends(get_db)):
    """List persons with red load rate."""
    from app.models.timesheet.models import Timesheet

    stmt = select(Timesheet.staff_id, func.sum(Timesheet.hours).label("total_hours")).where(
        Timesheet.check_status == "approved",
    ).group_by(Timesheet.staff_id)
    result = await db.execute(stmt)
    rows = result.all()

    warnings = []
    for staff_id, total_hours in rows:
        load_rate = (Decimal(str(total_hours)) / Decimal("176")) * 100
        if load_rate > 100 or load_rate < 70:
            p = await db.get(OutsourcePerson, staff_id)
            warnings.append({
                "personId": staff_id, "name": p.name if p else staff_id,
                "loadRate": round(float(load_rate), 1),
                "status": "overload" if load_rate > 100 else "underload",
            })

    return ApiResponse(code="SUCCESS", message="success", data=warnings)


# ═══════════════════════════════════════════════════════════════════════
# F-513: Efficiency Reports
# ═══════════════════════════════════════════════════════════════════════

@router.get("/reports/efficiency")
async def efficiency_report(
    period: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Person efficiency report."""
    stmt = select(OutsourcePerson).where(OutsourcePerson.pool_status.in_([0, 1]))
    result = await db.execute(stmt)
    persons = result.scalars().all()

    report = []
    for p in persons:
        from app.models.timesheet.models import Timesheet
        ts_stmt = select(func.sum(Timesheet.hours)).where(
            Timesheet.staff_id == p.person_id,
            Timesheet.check_status == "approved",
        )
        ts_result = await db.execute(ts_stmt)
        total_hours = ts_result.scalar() or 0

        perf_stmt = select(PerformanceEval).where(
            PerformanceEval.person_id == p.person_id,
        ).order_by(PerformanceEval.create_time.desc()).limit(1)
        perf_result = await db.execute(perf_stmt)
        latest_eval = perf_result.scalar_one_or_none()

        report.append({
            "personId": p.person_id, "name": p.name,
            "level": p.level, "department": p.department,
            "totalHours": float(total_hours),
            "overallScore": float(latest_eval.overall_score) if latest_eval and latest_eval.overall_score else None,
            "grade": latest_eval.grade if latest_eval else None,
        })

    return ApiResponse(code="SUCCESS", message="success", data=report)


# ═══════════════════════════════════════════════════════════════════════
# Outsourcing Management (Java /api/resource/outsourcing/* mapping)
# ═══════════════════════════════════════════════════════════════════════

@router.get("/outsourcing/pool/{pool_id}")
async def list_outsourcing_by_pool(
    pool_id: str,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List outsourcing staff by pool."""
    stmt = select(OutsourcePerson).where(OutsourcePerson.pool_status.in_([0, 1]))
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[_person_to_dict(p) for p in items],
    ))


@router.get("/outsourcing/{person_id}")
async def get_outsourcing_person(person_id: str, db: AsyncSession = Depends(get_db)):
    """Get outsourcing staff by ID."""
    return await get_person(person_id, db)


@router.post("/outsourcing")
async def create_outsourcing_person(req: PersonCreateRequest, db: AsyncSession = Depends(get_db)):
    """Add new outsourcing staff."""
    return await create_person(req, db)


@router.put("/outsourcing/{person_id}")
async def update_outsourcing_person(person_id: str, req: PersonUpdateRequest, db: AsyncSession = Depends(get_db)):
    """Update outsourcing staff."""
    return await update_person(person_id, req, db)


@router.post("/outsourcing/{person_id}/exit")
async def exit_outsourcing_person(person_id: str, db: AsyncSession = Depends(get_db)):
    """Mark staff as departed (exit)."""
    p = await db.get(OutsourcePerson, person_id)
    if not p:
        raise ResourceNotFoundError("OutsourcePerson", person_id)
    p.pool_status = 2
    p.exit_date = date_type.today()
    await db.flush()
    return ApiResponse(code="SUCCESS", message="人员已出场")


@router.get("/outsourcing/skills/{skill}")
async def list_by_skill(skill: str, db: AsyncSession = Depends(get_db)):
    """List active staff by skill."""
    stmt = select(OutsourcePerson).where(OutsourcePerson.pool_status.in_([0, 1]))
    result = await db.execute(stmt)
    persons = result.scalars().all()
    matched = []
    for p in persons:
        try:
            tags = json.loads(p.skill_tags) if p.skill_tags else []
            if any(skill.lower() in tag.lower() for tag in tags):
                matched.append(_person_to_dict(p))
        except (json.JSONDecodeError, TypeError):
            pass
    return ApiResponse(code="SUCCESS", message="success", data=matched)


# ═══════════════════════════════════════════════════════════════════════

@router.get("/pools")
async def list_pools(db: AsyncSession = Depends(get_db)):
    stmt = select(ResourcePool)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"poolId": p.pool_id, "poolName": p.pool_name,
         "managerId": p.manager_id, "description": p.description}
        for p in items
    ])


@router.get("/pool")
async def list_pool_alias(db: AsyncSession = Depends(get_db)):
    return await list_pools(db=db)


@router.post("/pools")
async def create_pool(req: PoolCreateRequest, db: AsyncSession = Depends(get_db)):
    pool = ResourcePool(
        pool_id=str(uuid.uuid4()), pool_name=req.pool_name,
        manager_id=req.manager_id, description=req.description,
    )
    db.add(pool)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"poolId": pool.pool_id})


@router.get("/leave")
async def list_leave(
    person_id: str | None = None, status: str | None = None,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(LeaveRequest).order_by(LeaveRequest.create_time.desc())
    if person_id:
        stmt = stmt.where(LeaveRequest.person_id == person_id)
    if status:
        stmt = stmt.where(LeaveRequest.status == status)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{
            "leaveId": lr.leave_id, "personId": lr.person_id,
            "leaveType": lr.leave_type,
            "startDate": str(lr.start_date) if lr.start_date else None,
            "endDate": str(lr.end_date) if lr.end_date else None,
            "days": lr.days, "reason": lr.reason,
            "status": lr.status, "approverId": lr.approver_id,
        } for lr in items],
    ))


@router.post("/leave")
async def create_leave(req: LeaveCreateRequest, db: AsyncSession = Depends(get_db)):
    lr = LeaveRequest(
        leave_id=str(uuid.uuid4()), person_id=req.person_id,
        leave_type=req.leave_type, start_date=req.start_date,
        end_date=req.end_date, days=req.days, reason=req.reason,
        status=req.status or "pending", approver_id=req.approver_id,
    )
    db.add(lr)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"leaveId": lr.leave_id})


@router.post("/leave/{leave_id}/approve")
async def approve_leave(leave_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(LeaveRequest).where(LeaveRequest.leave_id == leave_id)
    lr = (await db.execute(stmt)).scalar_one_or_none()
    if not lr:
        raise ResourceNotFoundError("LeaveRequest", leave_id)
    lr.status = "approved"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="审批通过")


@router.get("/replacements")
async def list_replacements(person_id: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(PersonnelReplacement)
    if person_id:
        stmt = stmt.where(PersonnelReplacement.person_id == person_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"replaceId": r.replace_id, "personId": r.person_id,
         "projectId": r.project_id, "reason": r.reason, "status": r.status}
        for r in items
    ])


@router.post("/replacements")
async def create_replacement(req: ReplacementCreateRequest, db: AsyncSession = Depends(get_db)):
    r = PersonnelReplacement(
        replace_id=str(uuid.uuid4()), person_id=req.person_id,
        project_id=req.project_id, reason=req.reason,
        status=req.status or "pending",
    )
    db.add(r)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"replaceId": r.replace_id})


@router.get("/replacements/{replace_id}")
async def get_replacement(replace_id: str, db: AsyncSession = Depends(get_db)):
    """Get replacement request detail."""
    r = await db.get(PersonnelReplacement, replace_id)
    if not r:
        raise ResourceNotFoundError("人员替换请求", replace_id)
    return ApiResponse(code="SUCCESS", message="success", data={
        "replaceId": r.replace_id, "personId": r.person_id,
        "projectId": r.project_id, "reason": r.reason,
        "status": r.status,
        "createTime": str(r.create_time) if hasattr(r, "create_time") and r.create_time else None,
    })


@router.put("/replacements/{replace_id}")
async def update_replacement(replace_id: str, req: ReplacementUpdateRequest, db: AsyncSession = Depends(get_db)):
    """Update replacement request."""
    r = await db.get(PersonnelReplacement, replace_id)
    if not r:
        raise ResourceNotFoundError("人员替换请求", replace_id)
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(r, field, value)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.post("/replacements/{replace_id}/approve")
async def approve_replacement(replace_id: str, req: ApproverRequest, db: AsyncSession = Depends(get_db)):
    """Approve a replacement request."""
    r = await db.get(PersonnelReplacement, replace_id)
    if not r:
        raise ResourceNotFoundError("人员替换请求", replace_id)
    r.status = "approved"
    r.approved_by = req.approved_by
    await db.flush()
    return ApiResponse(code="SUCCESS", message="人员替换已批准")


@router.post("/replacements/{replace_id}/complete")
async def complete_replacement(replace_id: str, db: AsyncSession = Depends(get_db)):
    """Mark replacement as complete."""
    r = await db.get(PersonnelReplacement, replace_id)
    if not r:
        raise ResourceNotFoundError("人员替换请求", replace_id)
    if r.status != "approved":
        raise ValidationError(message="Only approved replacements can be completed")
    r.status = "completed"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="人员替换已完成")


# ═══════════════════════════════════════════════════════════════════════
# Request / Response Schemas
# ═══════════════════════════════════════════════════════════════════════

# Alias for Pydantic model type annotations (avoids Python 3.14 forward-ref issues)
date = date_type


class PoolCreateRequest(BaseModel):
    pool_name: str
    manager_id: str | None = None
    description: str | None = None


class PersonCreateRequest(BaseModel):
    emp_code: str
    name: str
    id_card: str
    phone: str | None = None
    email: str | None = None
    skill_tags: list[str] | None = None
    level: int  # 1-4
    daily_rate: Decimal
    department: str | None = None
    pool_status: int | None = 0  # 0:可用 1:已分配 2:已退场
    current_project: str | None = None
    entry_date: Optional[date_type] = None
    background_check: int | None = None
    security_review: int | None = None
    confidentiality_agreement: int | None = None
    attendance_group: str | None = None


class PersonUpdateRequest(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    skill_tags: list[str] | None = None
    level: int | None = None
    daily_rate: Decimal | None = None
    department: str | None = None
    pool_status: int | None = None
    current_project: str | None = None
    entry_date: Optional[date_type] = None
    exit_date: Optional[date_type] = None
    background_check: int | None = None
    security_review: int | None = None
    confidentiality_agreement: int | None = None
    attendance_group: str | None = None


class SkillCreateRequest(BaseModel):
    person_id: str
    skill_name: str
    proficiency: int
    cert_name: str | None = None
    cert_date: Optional[date_type] = None
    expiry_date: Optional[date_type] = None


class SkillUpdateRequest(BaseModel):
    skill_name: str | None = None
    proficiency: int | None = None
    cert_name: str | None = None
    cert_date: Optional[date_type] = None
    expiry_date: Optional[date_type] = None


class PositionCreateRequest(BaseModel):
    pool_id: str
    position_name: str
    level: int
    skill_requirements: list[str] | None = None
    head_count: int | None = None
    department: str | None = None
    status: int | None = None


class PositionUpdateRequest(BaseModel):
    position_name: str | None = None
    level: int | None = None
    skill_requirements: list[str] | None = None
    head_count: int | None = None
    filled_count: int | None = None
    department: str | None = None
    status: int | None = None


class EntryExitRequest(BaseModel):
    pool_id: str | None = None
    date: Optional[date_type] = None
    exit_date: Optional[date_type] = None
    approved_by: str | None = None
    attendance_group: str | None = None


class ExitRequest(BaseModel):
    exit_date: Optional[date_type] = None
    approved_by: str | None = None


class ApproveRequest(BaseModel):
    approver_id: str
    date: Optional[date_type] = None
    attendance_group: str | None = None


class MatchRequest(BaseModel):
    position_id: str | None = None
    skill_requirements: list[str] | None = None
    experience_min: int | None = None


class AttendanceCheckRequest(BaseModel):
    person_id: str
    date: Optional[date_type] = None
    gps_lat: float | None = None
    gps_lng: float | None = None
    wifi_mac: str | None = None
    project_id: str | None = None


class ConfirmRequest(BaseModel):
    confirmed_by: str


class PerformanceEvaluateRequest(BaseModel):
    project_id: str | None = None
    evaluator_id: str | None = None
    pm_satisfaction: Decimal
    timesheet_compliance: Decimal
    task_completion: Decimal
    quality_metric: Decimal
    attendance_compliance: Decimal
    comments: str | None = None


class PerformanceUpdateRequest(BaseModel):
    pm_satisfaction: Decimal | None = None
    timesheet_compliance: Decimal | None = None
    task_completion: Decimal | None = None
    quality_metric: Decimal | None = None
    attendance_compliance: Decimal | None = None
    comments: str | None = None


class LeaveCreateRequest(BaseModel):
    person_id: str
    leave_type: str | None = None
    start_date: Optional[date_type] = None
    end_date: Optional[date_type] = None
    days: int | None = None
    reason: str | None = None
    status: str | None = None
    approver_id: str | None = None


class ReplacementCreateRequest(BaseModel):
    person_id: str
    project_id: str
    reason: str | None = None
    status: str | None = None


class ReplacementUpdateRequest(BaseModel):
    reason: str | None = None
    status: str | None = None
    project_id: str | None = None


class ApproverRequest(BaseModel):
    approved_by: str
