"""Timesheet API router — consolidates timesheet and work report controllers."""

from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ApiResponse, PageResult
from app.database import get_db
from app.exceptions import ResourceNotFoundError
from app.models.timesheet.models import Timesheet, TimesheetAttendance

router = APIRouter(tags=["timesheet"])


# ── Timesheets ───────────────────────────────────────────────────────

@router.get("")
async def list_timesheets(
    staff_id: str | None = None, project_id: str | None = None,
    check_status: str | None = None, work_date: str | None = None,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Timesheet).order_by(Timesheet.work_date.desc())
    if staff_id:
        stmt = stmt.where(Timesheet.staff_id == staff_id)
    if project_id:
        stmt = stmt.where(Timesheet.project_id == project_id)
    if check_status:
        stmt = stmt.where(Timesheet.check_status == check_status)
    if work_date:
        stmt = stmt.where(Timesheet.work_date == work_date)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{"timesheetId": t.timesheet_id, "staffId": t.staff_id, "projectId": t.project_id,
                 "workDate": str(t.work_date) if t.work_date else None,
                 "hours": float(t.hours) if t.hours else None,
                 "checkStatus": t.check_status, "attendanceCheckResult": t.attendance_check_result,
                 "remark": t.remark} for t in items],
    ))


@router.post("")
async def create_timesheet(req: TimesheetCreateRequest, db: AsyncSession = Depends(get_db)):
    ts = Timesheet(
        timesheet_id=str(uuid.uuid4()), staff_id=req.staff_id,
        project_id=req.project_id, work_date=req.work_date,
        hours=req.hours, check_status=req.check_status or "pending",
        attendance_check_result=req.attendance_check_result, remark=req.remark,
    )
    db.add(ts)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"timesheetId": ts.timesheet_id})


@router.put("/{timesheet_id}")
async def update_timesheet(timesheet_id: str, req: TimesheetUpdateRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Timesheet).where(Timesheet.timesheet_id == timesheet_id)
    ts = (await db.execute(stmt)).scalar_one_or_none()
    if not ts:
        raise ResourceNotFoundError("工时记录", timesheet_id)
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(ts, field, value)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.delete("/{timesheet_id}")
async def delete_timesheet(timesheet_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Timesheet).where(Timesheet.timesheet_id == timesheet_id)
    ts = (await db.execute(stmt)).scalar_one_or_none()
    if not ts:
        raise ResourceNotFoundError("工时记录", timesheet_id)
    await db.delete(ts)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.post("/{timesheet_id}/approve")
async def approve_timesheet(timesheet_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Timesheet).where(Timesheet.timesheet_id == timesheet_id)
    ts = (await db.execute(stmt)).scalar_one_or_none()
    if not ts:
        raise ResourceNotFoundError("工时记录", timesheet_id)
    ts.check_status = "approved"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="审批通过")


@router.post("/{timesheet_id}/reject")
async def reject_timesheet(timesheet_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Timesheet).where(Timesheet.timesheet_id == timesheet_id)
    ts = (await db.execute(stmt)).scalar_one_or_none()
    if not ts:
        raise ResourceNotFoundError("工时记录", timesheet_id)
    ts.check_status = "rejected"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="已拒绝")


# ── Attendance ───────────────────────────────────────────────────────

@router.get("/attendance")
async def list_attendance(
    user_id: str | None = None, date_from: str | None = None,
    date_to: str | None = None, db: AsyncSession = Depends(get_db),
):
    stmt = select(TimesheetAttendance)
    if user_id:
        stmt = stmt.where(TimesheetAttendance.user_id == user_id)
    if date_from:
        stmt = stmt.where(TimesheetAttendance.date >= date_from)
    if date_to:
        stmt = stmt.where(TimesheetAttendance.date <= date_to)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"attendanceId": a.attendance_id, "userId": a.user_id,
         "date": str(a.date) if a.date else None,
         "checkInTime": str(a.check_in_time) if a.check_in_time else None,
         "checkOutTime": str(a.check_out_time) if a.check_out_time else None,
         "status": a.status, "projectId": a.project_id} for a in items
    ])


# ── Work Reports ─────────────────────────────────────────────────────

@router.get("/reports")
async def work_reports(
    staff_id: str | None = None, project_id: str | None = None,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Generate work reports from timesheet data."""
    stmt = select(
        Timesheet.staff_id,
        Timesheet.project_id,
        func.sum(Timesheet.hours).label("total_hours"),
        func.count(Timesheet.timesheet_id).label("days"),
    ).group_by(Timesheet.staff_id, Timesheet.project_id)
    if staff_id:
        stmt = stmt.where(Timesheet.staff_id == staff_id)
    if project_id:
        stmt = stmt.where(Timesheet.project_id == project_id)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{"staffId": r[0], "projectId": r[1], "totalHours": float(r[2]) if r[2] else 0,
                 "days": r[3]} for r in items],
    ))


# ── Legacy aliases (frontend compatibility) ──────────────────────────

@router.get("/list")
async def list_timesheets_alias(
    staff_id: str | None = None, project_id: str | None = None,
    check_status: str | None = None, work_date: str | None = None,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await list_timesheets(staff_id=staff_id, project_id=project_id, check_status=check_status, work_date=work_date, page=page, size=size, db=db)


@router.post("/create")
async def create_timesheet_alias(req: TimesheetCreateRequest, db: AsyncSession = Depends(get_db)):
    return await create_timesheet(req, db)


@router.get("/approvals")
async def list_approvals(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    """List timesheets pending approval."""
    stmt = select(Timesheet).where(Timesheet.check_status == "pending").order_by(Timesheet.create_time.desc())
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{"timesheetId": t.timesheet_id, "staffId": t.staff_id, "projectId": t.project_id,
                  "workDate": str(t.work_date) if t.work_date else None, "hours": float(t.hours) if t.hours else 0,
                  "status": t.check_status} for t in items],
    ))


@router.post("/approvals/{approval_id}/approve")
async def approve_task(approval_id: str, db: AsyncSession = Depends(get_db)):
    from app.exceptions import ResourceNotFoundError
    ts = await db.get(Timesheet, approval_id)
    if not ts:
        raise ResourceNotFoundError("Timesheet", approval_id)
    ts.check_status = "approved"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.post("/approvals/{approval_id}/reject")
async def reject_task(approval_id: str, db: AsyncSession = Depends(get_db)):
    from app.exceptions import ResourceNotFoundError
    ts = await db.get(Timesheet, approval_id)
    if not ts:
        raise ResourceNotFoundError("Timesheet", approval_id)
    ts.check_status = "rejected"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


@router.post("/{timesheet_id}/submit")
async def submit_timesheet(timesheet_id: str, db: AsyncSession = Depends(get_db)):
    from app.exceptions import ResourceNotFoundError
    ts = await db.get(Timesheet, timesheet_id)
    if not ts:
        raise ResourceNotFoundError("Timesheet", timesheet_id)
    ts.check_status = "submitted"
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Request schemas ──────────────────────────────────────────────────

class TimesheetCreateRequest(BaseModel):
    staff_id: str
    project_id: str
    work_date: str
    hours: float
    check_status: str | None = None
    attendance_check_result: str | None = None
    remark: str | None = None

class TimesheetUpdateRequest(BaseModel):
    hours: float | None = None
    check_status: str | None = None
    attendance_check_result: str | None = None
    remark: str | None = None


# ── F-3011: Unreported Detection ─────────────────────────────────────

@router.get("/unreported")
async def list_unreported(
    staff_id: str | None = None, date_from: str | None = None,
    date_to: str | None = None, db: AsyncSession = Depends(get_db),
):
    """检测未填报工时的人员和日期."""
    from app.models.resource.models import OutsourcePerson
    stmt = select(OutsourcePerson).where(OutsourcePerson.pool_status.in_([0, 1]))
    if staff_id:
        stmt = stmt.where(OutsourcePerson.person_id == staff_id)
    result = await db.execute(stmt)
    persons = result.scalars().all()

    from datetime import datetime, timedelta
    end = datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else datetime.utcnow().date()
    start = datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else end - timedelta(days=6)
    workdays = [d for d in _iter_workdays(start, end)]

    unreported = []
    for p in persons:
        ts_stmt = select(Timesheet.work_date).where(
            Timesheet.staff_id == p.person_id,
            Timesheet.work_date >= start,
            Timesheet.work_date <= end,
        )
        ts_result = await db.execute(ts_stmt)
        reported_dates = {str(r[0]) for r in ts_result}
        missing = [str(d) for d in workdays if str(d) not in reported_dates]
        if missing:
            unreported.append({
                "personId": p.person_id, "name": p.name,
                "missingDates": missing, "missingDays": len(missing),
            })
    return ApiResponse(code="SUCCESS", message="success", data={"unreported": unreported})


def _iter_workdays(start, end):
    from datetime import timedelta
    current = start
    while current <= end:
        if current.weekday() < 5:  # Mon-Fri
            yield current
        current += timedelta(days=1)


# ── F-3012: Anomaly Detection ────────────────────────────────────────

@router.get("/anomalies")
async def detect_anomalies(
    date_from: str | None = None, date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """检测工时填报异常（超时报、负数、异常高/低）."""
    stmt = select(Timesheet)
    if date_from:
        stmt = stmt.where(Timesheet.work_date >= date_from)
    if date_to:
        stmt = stmt.where(Timesheet.work_date <= date_to)
    result = await db.execute(stmt)
    items = result.scalars().all()

    anomalies = []
    for ts in items:
        hours = float(ts.hours) if ts.hours else 0
        if hours > 16:
            anomalies.append({
                "timesheetId": ts.timesheet_id, "staffId": ts.staff_id,
                "workDate": str(ts.work_date), "hours": hours,
                "type": "excessive_hours",
                "message": f"单日工时 {hours}h 超过16小时阈值",
            })
        elif hours <= 0:
            anomalies.append({
                "timesheetId": ts.timesheet_id, "staffId": ts.staff_id,
                "workDate": str(ts.work_date), "hours": hours,
                "type": "invalid_hours",
                "message": f"工时报错: {hours}h",
            })

    return ApiResponse(code="SUCCESS", message="success", data={"anomalies": anomalies})


# ── F-3013: Weekly Report ────────────────────────────────────────────

@router.get("/weekly-report/{staff_id}")
async def generate_weekly_report(
    staff_id: str, week_start: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """生成个人周报."""
    from datetime import datetime, timedelta
    if week_start:
        start = datetime.strptime(week_start, "%Y-%m-%d").date()
    else:
        today = datetime.utcnow().date()
        start = today - timedelta(days=today.weekday())

    end = start + timedelta(days=6)
    stmt = select(Timesheet).where(
        Timesheet.staff_id == staff_id,
        Timesheet.work_date >= start,
        Timesheet.work_date <= end,
    ).order_by(Timesheet.work_date)
    result = await db.execute(stmt)
    items = result.scalars().all()

    total_hours = sum(float(ts.hours) if ts.hours else 0 for ts in items)
    return ApiResponse(code="SUCCESS", message="success", data={
        "staffId": staff_id, "weekStart": str(start), "weekEnd": str(end),
        "totalHours": round(total_hours, 1),
        "entries": [
            {"date": str(ts.work_date), "projectId": ts.project_id,
             "hours": float(ts.hours) if ts.hours else 0,
             "remark": ts.remark}
            for ts in items
        ],
    })
