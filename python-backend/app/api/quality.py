"""Quality API router — consolidates defect and metric controllers."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ApiResponse, PageResult
from app.database import get_db
from app.exceptions import ResourceNotFoundError
from app.models.quality.models import QualityDefect, QualityMetric

router = APIRouter(tags=["quality"])


# ── Defects ──────────────────────────────────────────────────────────

@router.get("/defects")
async def list_defects(
    project_id: str | None = None, severity: str | None = None,
    status: str | None = None, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(QualityDefect).order_by(QualityDefect.create_time.desc())
    if project_id:
        stmt = stmt.where(QualityDefect.project_id == project_id)
    if severity:
        stmt = stmt.where(QualityDefect.severity == severity)
    if status:
        stmt = stmt.where(QualityDefect.status == status)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{"defectId": d.defect_id, "projectId": d.project_id, "defectName": d.defect_name,
                 "defectType": d.defect_type, "severity": d.severity, "status": d.status,
                 "foundBy": d.found_by, "assignedTo": d.assigned_to,
                 "foundDate": str(d.found_date) if d.found_date else None,
                 "fixedDate": str(d.fixed_date) if d.fixed_date else None,
                 "description": d.description} for d in items],
    ))


@router.post("/defects")
async def create_defect(req: DefectCreateRequest, db: AsyncSession = Depends(get_db)):
    d = QualityDefect(
        defect_id=str(uuid.uuid4()), project_id=req.project_id,
        defect_name=req.defect_name, defect_type=req.defect_type,
        severity=req.severity, status=req.status or "open",
        found_by=req.found_by, assigned_to=req.assigned_to,
        found_date=req.found_date, fixed_date=req.fixed_date,
        description=req.description,
    )
    db.add(d)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"defectId": d.defect_id})


@router.put("/defects/{defect_id}")
async def update_defect(defect_id: str, req: DefectUpdateRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(QualityDefect).where(QualityDefect.defect_id == defect_id)
    d = (await db.execute(stmt)).scalar_one_or_none()
    if not d:
        raise ResourceNotFoundError("缺陷", defect_id)
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(d, field, value)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Metrics ──────────────────────────────────────────────────────────

@router.get("/metrics")
async def list_metrics(
    project_id: str | None = None, db: AsyncSession = Depends(get_db),
):
    stmt = select(QualityMetric)
    if project_id:
        stmt = stmt.where(QualityMetric.project_id == project_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"metricId": m.metric_id, "projectId": m.project_id, "metricName": m.metric_name,
         "metricValue": float(m.metric_value) if m.metric_value else None,
         "targetValue": float(m.target_value) if m.target_value else None,
         "measurementDate": str(m.measurement_date) if m.measurement_date else None,
         "unit": m.unit} for m in items
    ])


@router.post("/metrics")
async def create_metric(req: MetricCreateRequest, db: AsyncSession = Depends(get_db)):
    m = QualityMetric(
        metric_id=str(uuid.uuid4()), project_id=req.project_id,
        metric_name=req.metric_name, metric_value=req.metric_value,
        target_value=req.target_value, measurement_date=req.measurement_date,
        unit=req.unit,
    )
    db.add(m)
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success", data={"metricId": m.metric_id})


@router.post("/defect/{defect_id}/close")
async def close_defect(defect_id: str, db: AsyncSession = Depends(get_db)):
    """Close a quality defect."""
    d = await db.get(QualityDefect, defect_id)
    if not d:
        raise ResourceNotFoundError("缺陷", defect_id)
    d.status = "closed"
    d.fixed_date = datetime.now(timezone.utc).date()
    await db.flush()
    return ApiResponse(code="SUCCESS", message="缺陷已关闭")


@router.get("/metrics/{project_id}")
async def get_metrics_by_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get quality metrics for a specific project."""
    stmt = select(QualityMetric).where(QualityMetric.project_id == project_id).order_by(
        QualityMetric.measurement_date.desc()
    )
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"metricId": m.metric_id, "projectId": m.project_id, "metricName": m.metric_name,
         "metricValue": float(m.metric_value) if m.metric_value else None,
         "targetValue": float(m.target_value) if m.target_value else None,
         "measurementDate": str(m.measurement_date) if m.measurement_date else None,
         "unit": m.unit} for m in items
    ])


# ── Legacy aliases (frontend compatibility) ──────────────────────────

@router.get("/defect/list")
async def list_defects_alias(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
                              project_id: str | None = None, status: str | None = None,
                              db: AsyncSession = Depends(get_db)):
    return await list_defects(page=page, size=size, project_id=project_id, status=status, db=db)


@router.post("/defect/{defect_id}/resolve")
async def resolve_defect(defect_id: str, db: AsyncSession = Depends(get_db)):
    from app.exceptions import ResourceNotFoundError
    d = await db.get(QualityDefect, defect_id)
    if not d:
        raise ResourceNotFoundError("Defect", defect_id)
    d.status = "closed"
    d.fixed_date = datetime.now(timezone.utc).date()
    await db.flush()
    return ApiResponse(code="SUCCESS", message="success")


# ── Request schemas ──────────────────────────────────────────────────

class DefectCreateRequest(BaseModel):
    project_id: str
    defect_name: str
    defect_type: str | None = None
    severity: str | None = None
    status: str | None = None
    found_by: str | None = None
    assigned_to: str | None = None
    found_date: str | None = None
    fixed_date: str | None = None
    description: str | None = None

class DefectUpdateRequest(BaseModel):
    defect_name: str | None = None
    defect_type: str | None = None
    severity: str | None = None
    status: str | None = None
    assigned_to: str | None = None
    fixed_date: str | None = None
    description: str | None = None

class MetricCreateRequest(BaseModel):
    project_id: str
    metric_name: str
    metric_value: float | None = None
    target_value: float | None = None
    measurement_date: str | None = None
    unit: str | None = None


# ── F-1010: Compliance Audit & Risk Control ──────────────────────────

@router.post("/compliance/check")
async def compliance_check(req: ComplianceCheckRequest, db: AsyncSession = Depends(get_db)):
    """合规审计风控 (F-1010)."""
    checks = []

    # Quality defect compliance
    stmt = select(func.count(QualityDefect.defect_id)).where(
        QualityDefect.project_id == req.project_id, QualityDefect.status == "open"
    )
    open_defects = (await db.execute(stmt)).scalar() or 0
    checks.append({
        "item": "未关闭缺陷",
        "status": "pass" if open_defects < 5 else "warning" if open_defects < 10 else "fail",
        "detail": f"当前有 {open_defects} 个未关闭缺陷",
    })

    # Metric compliance
    stmt = select(func.count(QualityMetric.metric_id)).where(
        QualityMetric.project_id == req.project_id,
        QualityMetric.metric_value < QualityMetric.target_value,
    )
    below_target = (await db.execute(stmt)).scalar() or 0
    checks.append({
        "item": "指标达标率",
        "status": "pass" if below_target == 0 else "warning",
        "detail": f"{below_target} 项指标未达标",
    })

    overall = all(c["status"] == "pass" for c in checks)
    return ApiResponse(code="SUCCESS", message="success", data={
        "projectId": req.project_id,
        "overall": "pass" if overall else "fail",
        "checks": checks,
    })


@router.get("/risk-report")
async def quality_risk_report(project_id: str, db: AsyncSession = Depends(get_db)):
    """质量风险报告 (F-1010)."""
    total_defects = (await db.execute(select(func.count(QualityDefect.defect_id)).where(
        QualityDefect.project_id == project_id
    ))).scalar() or 0
    severity_breakdown = []
    for sev in ["critical", "high", "medium", "low"]:
        count = (await db.execute(select(func.count(QualityDefect.defect_id)).where(
            QualityDefect.project_id == project_id, QualityDefect.severity == sev
        ))).scalar() or 0
        severity_breakdown.append({"severity": sev, "count": count})

    return ApiResponse(code="SUCCESS", message="success", data={
        "projectId": project_id,
        "totalDefects": total_defects,
        "severityBreakdown": severity_breakdown,
    })


class ComplianceCheckRequest(BaseModel):
    project_id: str
    check_scope: str | None = None
