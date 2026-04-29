"""Audit API router — replicates AuditLogController."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ApiResponse, PageResult
from app.database import get_db
from app.models.audit.models import AuditLogEntry

router = APIRouter(tags=["audit"])


@router.get("/logs")
async def list_audit_logs(
    user_id: str | None = None, action: str | None = None,
    resource_type: str | None = None,
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(AuditLogEntry).order_by(AuditLogEntry.timestamp.desc())
    if user_id:
        stmt = stmt.where(AuditLogEntry.user_id == user_id)
    if action:
        stmt = stmt.where(AuditLogEntry.action == action)
    if resource_type:
        stmt = stmt.where(AuditLogEntry.resource_type == resource_type)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=PageResult(
        total=total, page=page, size=size,
        records=[{"entryId": e.entry_id, "auditId": e.audit_id, "userId": e.user_id,
                 "action": e.action, "resourceType": e.resource_type,
                 "resourceId": e.resource_id, "details": e.details,
                 "ipAddress": e.ip_address, "timestamp": str(e.timestamp) if e.timestamp else None}
               for e in items],
    ))


@router.get("/logs/export")
async def export_audit_logs(
    user_id: str | None = None, action: str | None = None,
    date_from: str | None = None, date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """导出审计日志为CSV/JSON格式."""
    stmt = select(AuditLogEntry).order_by(AuditLogEntry.timestamp.desc()).limit(1000)
    if user_id:
        stmt = stmt.where(AuditLogEntry.user_id == user_id)
    if action:
        stmt = stmt.where(AuditLogEntry.action == action)
    if date_from:
        stmt = stmt.where(AuditLogEntry.timestamp >= date_from)
    if date_to:
        stmt = stmt.where(AuditLogEntry.timestamp <= date_to)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"entryId": e.entry_id, "userId": e.user_id, "action": e.action,
         "resourceType": e.resource_type, "resourceId": e.resource_id,
         "ipAddress": e.ip_address, "timestamp": str(e.timestamp) if e.timestamp else None}
        for e in items
    ])


@router.get("/summary")
async def audit_summary(db: AsyncSession = Depends(get_db)):
    """审计日志摘要统计."""
    total_stmt = select(func.count(AuditLogEntry.entry_id))
    total = (await db.execute(total_stmt)).scalar() or 0

    action_stmt = select(AuditLogEntry.action, func.count(AuditLogEntry.entry_id)).group_by(AuditLogEntry.action)
    action_result = await db.execute(action_stmt)
    action_counts = [{"action": r[0], "count": r[1]} for r in action_result.all()]

    today_total = (await db.execute(select(func.count(AuditLogEntry.entry_id)).where(
        func.date(AuditLogEntry.timestamp) == func.current_date(),
    ))).scalar() or 0

    return ApiResponse(code="SUCCESS", message="success", data={
        "totalEntries": total,
        "todayEntries": today_total,
        "actionBreakdown": action_counts,
    })


@router.get("/recent")
async def recent_operations(limit: int = Query(50, ge=1, le=200), db: AsyncSession = Depends(get_db)):
    """最近操作记录."""
    stmt = select(AuditLogEntry).order_by(AuditLogEntry.timestamp.desc()).limit(limit)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ApiResponse(code="SUCCESS", message="success", data=[
        {"entryId": e.entry_id, "userId": e.user_id, "action": e.action,
         "resourceType": e.resource_type, "resourceId": e.resource_id,
         "timestamp": str(e.timestamp) if e.timestamp else None}
        for e in items
    ])
