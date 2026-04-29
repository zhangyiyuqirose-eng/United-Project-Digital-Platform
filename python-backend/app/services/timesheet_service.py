"""Timesheet domain service — extracted business logic from router.

Extends BaseService for standard Timesheet CRUD and adds approval workflow
methods plus monthly reporting.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import PageResult
from app.models.timesheet.models import Timesheet
from app.services.base import BaseService


class TimesheetService(BaseService[Timesheet]):
    """Encapsulates all timesheet-domain database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Timesheet)

    # ── Approval workflow ───────────────────────────────────────────────

    async def submit_for_approval(self, timesheet_id: str) -> dict:
        """Submit a draft timesheet for approval."""
        ts = await self.get_or_404(timesheet_id)
        ts.check_status = "submitted"
        await self.db.flush()
        return {
            "timesheetId": ts.timesheet_id,
            "status": ts.check_status,
        }

    async def approve(self, timesheet_id: str, approver_id: str) -> dict:
        """Approve a submitted timesheet."""
        ts = await self.get_or_404(timesheet_id)
        ts.check_status = "approved"
        await self.db.flush()
        return {
            "timesheetId": ts.timesheet_id,
            "status": ts.check_status,
            "approverId": approver_id,
        }

    async def reject(self, timesheet_id: str, reason: str) -> dict:
        """Reject a submitted timesheet with a reason."""
        ts = await self.get_or_404(timesheet_id)
        ts.check_status = "rejected"
        ts.attendance_check_result = reason
        await self.db.flush()
        return {
            "timesheetId": ts.timesheet_id,
            "status": ts.check_status,
            "reason": reason,
        }

    # ── Entry creation ──────────────────────────────────────────────────

    async def create_entry(
        self,
        staff_id: str,
        project_id: str,
        work_date: date | str,
        hours: float,
        remark: str | None = None,
    ) -> dict:
        """Create a new timesheet entry."""
        ts = Timesheet(
            timesheet_id=str(uuid.uuid4()),
            staff_id=staff_id,
            project_id=project_id,
            work_date=work_date if isinstance(work_date, date) else date.fromisoformat(work_date),
            hours=hours,
            check_status="pending",
            remark=remark,
        )
        self.db.add(ts)
        await self.db.flush()
        return {"timesheetId": ts.timesheet_id}

    # ── Monthly report ──────────────────────────────────────────────────

    async def get_monthly_report(self, year: int, month: int) -> dict:
        """Aggregate hours and entry counts for a calendar month."""
        stmt = select(Timesheet).where(
            extract("year", Timesheet.work_date) == year,
            extract("month", Timesheet.work_date) == month,
        )
        result = await self.db.execute(stmt)
        entries = result.scalars().all()

        total_hours = sum(float(e.hours or 0) for e in entries)

        # Group by staff
        by_staff: dict[str, dict] = {}
        for e in entries:
            sid = e.staff_id
            if sid not in by_staff:
                by_staff[sid] = {"staffId": sid, "totalHours": 0.0, "entries": 0, "approved": 0, "rejected": 0}
            by_staff[sid]["totalHours"] += float(e.hours or 0)
            by_staff[sid]["entries"] += 1
            if e.check_status == "approved":
                by_staff[sid]["approved"] += 1
            elif e.check_status == "rejected":
                by_staff[sid]["rejected"] += 1

        return {
            "year": year,
            "month": month,
            "totalHours": round(total_hours, 1),
            "totalEntries": len(entries),
            "byStaff": sorted(by_staff.values(), key=lambda x: x["totalHours"], reverse=True),
        }

    # ── Approvals queue ─────────────────────────────────────────────────

    async def list_pending_approvals(self, page: int = 1, size: int = 10) -> PageResult:
        """List timesheets pending approval."""
        base = select(Timesheet).where(
            Timesheet.check_status == "pending"
        ).order_by(Timesheet.create_time.desc())

        total = await self.db.scalar(
            select(func.count()).select_from(base.subquery())
        )
        offset = (page - 1) * size
        result = await self.db.execute(base.offset(offset).limit(size))

        return PageResult(
            total=total or 0,
            page=page,
            size=size,
            records=result.scalars().all(),
        )

    # ── Anomaly detection ───────────────────────────────────────────────

    async def detect_anomalies(
        self, date_from: date | None = None, date_to: date | None = None
    ) -> list[dict]:
        """Flag timesheets with excessive (>16h) or invalid (<=0h) hours."""
        stmt = select(Timesheet)
        if date_from:
            stmt = stmt.where(Timesheet.work_date >= date_from)
        if date_to:
            stmt = stmt.where(Timesheet.work_date <= date_to)
        result = await self.db.execute(stmt)
        entries = result.scalars().all()

        anomalies: list[dict] = []
        for ts in entries:
            hours = float(ts.hours or 0)
            if hours > 16:
                anomalies.append({
                    "timesheetId": ts.timesheet_id,
                    "staffId": ts.staff_id,
                    "workDate": str(ts.work_date) if ts.work_date else None,
                    "hours": hours,
                    "type": "excessive_hours",
                    "message": f"Single-day hours {hours}h exceeds 16h threshold",
                })
            elif hours <= 0:
                anomalies.append({
                    "timesheetId": ts.timesheet_id,
                    "staffId": ts.staff_id,
                    "workDate": str(ts.work_date) if ts.work_date else None,
                    "hours": hours,
                    "type": "invalid_hours",
                    "message": f"Invalid hours: {hours}h",
                })

        return anomalies
