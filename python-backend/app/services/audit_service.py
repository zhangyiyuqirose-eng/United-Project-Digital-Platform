"""Audit domain service — extracted business logic from router.

Extends BaseService for standard AuditLogEntry CRUD and adds audit-specific
query methods for user/module filtering, summary, and CSV export.
"""

from __future__ import annotations

import csv
import io
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import PageResult
from app.models.audit.models import AuditLogEntry
from app.services.base import BaseService


class AuditService(BaseService[AuditLogEntry]):
    """Encapsulates all audit-domain database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, AuditLogEntry)

    # ── Specialized queries ─────────────────────────────────────────────

    async def get_by_user(
        self, user_id: str, page: int = 1, limit: int = 20
    ) -> PageResult:
        """Return paginated audit entries for a specific user."""
        base = (
            select(AuditLogEntry)
            .where(AuditLogEntry.user_id == user_id)
            .order_by(AuditLogEntry.timestamp.desc())
        )
        total = await self.db.scalar(
            select(func.count()).select_from(base.subquery())
        )
        offset = (page - 1) * limit
        result = await self.db.execute(base.offset(offset).limit(limit))

        return PageResult(
            total=total or 0,
            page=page,
            size=limit,
            records=result.scalars().all(),
        )

    async def get_by_module(
        self, module: str, page: int = 1, limit: int = 20
    ) -> PageResult:
        """Return paginated audit entries filtered by resource_type (module)."""
        base = (
            select(AuditLogEntry)
            .where(AuditLogEntry.resource_type == module)
            .order_by(AuditLogEntry.timestamp.desc())
        )
        total = await self.db.scalar(
            select(func.count()).select_from(base.subquery())
        )
        offset = (page - 1) * limit
        result = await self.db.execute(base.offset(offset).limit(limit))

        return PageResult(
            total=total or 0,
            page=page,
            size=limit,
            records=result.scalars().all(),
        )

    async def get_summary(
        self, start_date: date | str | None = None, end_date: date | str | None = None
    ) -> dict:
        """Return summary statistics for a date range."""
        base = select(AuditLogEntry)
        if start_date:
            d = start_date if isinstance(start_date, date) else date.fromisoformat(str(start_date))
            base = base.where(AuditLogEntry.timestamp >= d)
        if end_date:
            d = end_date if isinstance(end_date, date) else date.fromisoformat(str(end_date))
            base = base.where(AuditLogEntry.timestamp <= d)

        # Total count
        total = await self.db.scalar(
            select(func.count()).select_from(base.subquery())
        )

        if not total:
            return {
                "totalEntries": 0,
                "startDate": str(start_date) if start_date else None,
                "endDate": str(end_date) if end_date else None,
                "byAction": [],
                "byResourceType": [],
                "byUser": [],
            }

        # Breakdown by action
        action_stmt = (
            select(AuditLogEntry.action, func.count(AuditLogEntry.entry_id))
            .where(base.whereclause if hasattr(base, "whereclause") else True)
            .group_by(AuditLogEntry.action)
            .order_by(func.count(AuditLogEntry.entry_id).desc())
        )
        # Rebuild with proper filter context
        action_base = select(
            AuditLogEntry.action, func.count(AuditLogEntry.entry_id)
        ).group_by(AuditLogEntry.action)
        if start_date:
            d = start_date if isinstance(start_date, date) else date.fromisoformat(str(start_date))
            action_base = action_base.where(AuditLogEntry.timestamp >= d)
        if end_date:
            d = end_date if isinstance(end_date, date) else date.fromisoformat(str(end_date))
            action_base = action_base.where(AuditLogEntry.timestamp <= d)

        action_result = await self.db.execute(action_base)
        by_action = [{"action": r[0], "count": r[1]} for r in action_result.all()]

        # Breakdown by resource type
        resource_base = select(
            AuditLogEntry.resource_type, func.count(AuditLogEntry.entry_id)
        ).group_by(AuditLogEntry.resource_type)
        if start_date:
            d = start_date if isinstance(start_date, date) else date.fromisoformat(str(start_date))
            resource_base = resource_base.where(AuditLogEntry.timestamp >= d)
        if end_date:
            d = end_date if isinstance(end_date, date) else date.fromisoformat(str(end_date))
            resource_base = resource_base.where(AuditLogEntry.timestamp <= d)

        resource_result = await self.db.execute(resource_base)
        by_resource_type = [{"resourceType": r[0], "count": r[1]} for r in resource_result.all()]

        # Top users
        user_base = select(
            AuditLogEntry.user_id, func.count(AuditLogEntry.entry_id)
        ).group_by(AuditLogEntry.user_id).order_by(
            func.count(AuditLogEntry.entry_id).desc()
        ).limit(20)
        if start_date:
            d = start_date if isinstance(start_date, date) else date.fromisoformat(str(start_date))
            user_base = user_base.where(AuditLogEntry.timestamp >= d)
        if end_date:
            d = end_date if isinstance(end_date, date) else date.fromisoformat(str(end_date))
            user_base = user_base.where(AuditLogEntry.timestamp <= d)

        user_result = await self.db.execute(user_base)
        by_user = [{"userId": r[0], "count": r[1]} for r in user_result.all()]

        return {
            "totalEntries": total or 0,
            "startDate": str(start_date) if start_date else None,
            "endDate": str(end_date) if end_date else None,
            "byAction": by_action,
            "byResourceType": by_resource_type,
            "byUser": by_user,
        }

    async def export_csv(
        self, start_date: date | str | None = None, end_date: date | str | None = None
    ) -> str:
        """Export audit entries to CSV format string."""
        base = select(AuditLogEntry).order_by(AuditLogEntry.timestamp.desc())
        if start_date:
            d = start_date if isinstance(start_date, date) else date.fromisoformat(str(start_date))
            base = base.where(AuditLogEntry.timestamp >= d)
        if end_date:
            d = end_date if isinstance(end_date, date) else date.fromisoformat(str(end_date))
            base = base.where(AuditLogEntry.timestamp <= d)

        result = await self.db.execute(base)
        entries = result.scalars().all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "entryId", "auditId", "userId", "action",
            "resourceType", "resourceId", "details",
            "ipAddress", "timestamp",
        ])
        for e in entries:
            writer.writerow([
                e.entry_id,
                e.audit_id or "",
                e.user_id or "",
                e.action or "",
                e.resource_type or "",
                e.resource_id or "",
                e.details or "",
                e.ip_address or "",
                str(e.timestamp) if e.timestamp else "",
            ])

        return output.getvalue()

    # ── Convenience: log an action ──────────────────────────────────────

    async def log_action(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        details: str | None = None,
        ip_address: str | None = None,
    ) -> dict:
        """Write an audit log entry."""
        entry = AuditLogEntry(
            entry_id=str(uuid.uuid4()),
            audit_id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            timestamp=datetime.utcnow(),
        )
        self.db.add(entry)
        await self.db.flush()
        return {"entryId": entry.entry_id}
