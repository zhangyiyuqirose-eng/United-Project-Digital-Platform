"""Report generation and download API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ApiResponse, PageResult
from app.database import get_db
from app.dependencies import get_current_user
from app.services.report_service import ReportService

router = APIRouter(tags=["report"])

REPORT_TYPE_MAP = {
    "project": ("Project Report", "project-report.xlsx"),
    "cost": ("Cost Report", "cost-report.xlsx"),
    "timesheet": ("Timesheet Report", "timesheet-report.xlsx"),
    "resource": ("Resource Report", "resource-report.xlsx"),
    "portfolio": ("Portfolio Report", "portfolio-report.xlsx"),
}


@router.get("/project/{project_id}/download")
async def download_project_report(
    project_id: str,
    format: str = Query(default="xlsx"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ReportService(db)
    data = await service.generate_project_report(project_id)
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="project-report-{project_id}.xlsx"'},
    )


@router.get("/cost/{project_id}/download")
async def download_cost_report(
    project_id: str,
    format: str = Query(default="xlsx"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ReportService(db)
    data = await service.generate_cost_report(project_id)
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="cost-report-{project_id}.xlsx"'},
    )


@router.get("/timesheet/download")
async def download_timesheet_report(
    staff_id: str = Query(...),
    month: str | None = Query(default=None),
    format: str = Query(default="xlsx"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ReportService(db)
    data = await service.generate_timesheet_report(staff_id, month)
    month_suffix = f"-{month}" if month else ""
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="timesheet-report-{staff_id}{month_suffix}.xlsx"'},
    )


@router.get("/resource/download")
async def download_resource_report(
    pool_id: str = Query(...),
    format: str = Query(default="xlsx"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ReportService(db)
    data = await service.generate_resource_report(pool_id)
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="resource-report-{pool_id}.xlsx"'},
    )


@router.get("/portfolio/download")
async def download_portfolio_report(
    format: str = Query(default="xlsx"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ReportService(db)
    data = await service.generate_portfolio_report()
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="portfolio-report.xlsx"'},
    )


@router.get("/list")
async def list_reports(
    type: str | None = Query(default=None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    from sqlalchemy import func, select

    from app.models.report.models import ReportHistory

    stmt = select(ReportHistory).order_by(ReportHistory.create_time.desc())
    if type:
        stmt = stmt.where(ReportHistory.report_type == type)

    total_result = await db.execute(
        select(func.count()).select_from(stmt.subquery())
    )
    total = total_result.scalar() or 0

    offset = (page - 1) * size
    result = await db.execute(stmt.offset(offset).limit(size))
    items = result.scalars().all()

    records = [
        {
            "id": r.report_id,
            "type": r.report_type,
            "name": r.file_name,
            "createdAt": r.create_time.isoformat() if r.create_time else "",
            "createdBy": r.created_by or "",
            "status": r.status,
        }
        for r in items
    ]

    return ApiResponse(
        code="SUCCESS",
        message="success",
        data=PageResult(total=total, page=page, size=size, records=records),
    )
