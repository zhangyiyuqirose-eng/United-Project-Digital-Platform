"""Quality domain service — handles QualityDefect and QualityMetric CRUD.

Does NOT extend BaseService because it manages two separate models.
"""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import PageResult
from app.exceptions import ResourceNotFoundError
from app.models.quality.models import QualityDefect, QualityMetric


class QualityService:
    """Encapsulates all quality-domain database operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── QualityDefect CRUD ──────────────────────────────────────────────

    async def list_defects(
        self,
        project_id: str | None = None,
        status: str | None = None,
        severity: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> PageResult:
        base = select(QualityDefect).order_by(QualityDefect.create_time.desc())
        if project_id:
            base = base.where(QualityDefect.project_id == project_id)
        if status:
            base = base.where(QualityDefect.status == status)
        if severity:
            base = base.where(QualityDefect.severity == severity)

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

    async def get_defect(self, defect_id: str) -> QualityDefect:
        return await self._defect_or_404(defect_id)

    async def create_defect(
        self,
        project_id: str,
        defect_name: str,
        defect_type: str | None = None,
        severity: str | None = None,
        found_by: str | None = None,
        assigned_to: str | None = None,
        found_date: date | None = None,
        description: str | None = None,
    ) -> dict:
        defect = QualityDefect(
            defect_id=str(uuid.uuid4()),
            project_id=project_id,
            defect_name=defect_name,
            defect_type=defect_type,
            severity=severity,
            status="open",
            found_by=found_by,
            assigned_to=assigned_to,
            found_date=found_date,
            description=description,
        )
        self.db.add(defect)
        await self.db.flush()
        return {"defectId": defect.defect_id}

    async def update_defect(self, defect_id: str, **kwargs) -> QualityDefect:
        defect = await self._defect_or_404(defect_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(defect, k):
                setattr(defect, k, v)
        await self.db.flush()
        return defect

    async def delete_defect(self, defect_id: str) -> None:
        defect = await self._defect_or_404(defect_id)
        await self.db.delete(defect)
        await self.db.flush()

    async def fix_defect(self, defect_id: str, fixed_date: date | None = None) -> dict:
        """Mark a defect as fixed."""
        defect = await self._defect_or_404(defect_id)
        defect.status = "fixed"
        defect.fixed_date = fixed_date or date.today()
        await self.db.flush()
        return {"defectId": defect.defect_id, "status": defect.status}

    async def close_defect(self, defect_id: str) -> dict:
        """Mark a defect as closed (verified fix)."""
        defect = await self._defect_or_404(defect_id)
        defect.status = "closed"
        await self.db.flush()
        return {"defectId": defect.defect_id, "status": defect.status}

    # ── QualityMetric CRUD ──────────────────────────────────────────────

    async def list_metrics(
        self, project_id: str | None = None, page: int = 1, size: int = 20
    ) -> PageResult:
        base = select(QualityMetric).order_by(QualityMetric.measurement_date.desc())
        if project_id:
            base = base.where(QualityMetric.project_id == project_id)

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

    async def get_metric(self, metric_id: str) -> QualityMetric:
        return await self._metric_or_404(metric_id)

    async def create_metric(
        self,
        project_id: str,
        metric_name: str,
        metric_value: float | None = None,
        target_value: float | None = None,
        measurement_date: date | None = None,
        unit: str | None = None,
    ) -> dict:
        metric = QualityMetric(
            metric_id=str(uuid.uuid4()),
            project_id=project_id,
            metric_name=metric_name,
            metric_value=metric_value,
            target_value=target_value,
            measurement_date=measurement_date,
            unit=unit,
        )
        self.db.add(metric)
        await self.db.flush()
        return {"metricId": metric.metric_id}

    async def update_metric(self, metric_id: str, **kwargs) -> QualityMetric:
        metric = await self._metric_or_404(metric_id)
        for k, v in kwargs.items():
            if v is not None and hasattr(metric, k):
                setattr(metric, k, v)
        await self.db.flush()
        return metric

    async def delete_metric(self, metric_id: str) -> None:
        metric = await self._metric_or_404(metric_id)
        await self.db.delete(metric)
        await self.db.flush()

    # ── Project quality summary ─────────────────────────────────────────

    async def get_project_quality_summary(self, project_id: str) -> dict:
        """Return a combined quality summary (defect counts + latest metrics)."""
        # Defect counts by status
        defect_stmt = select(
            QualityDefect.status, func.count(QualityDefect.defect_id)
        ).where(QualityDefect.project_id == project_id).group_by(QualityDefect.status)
        defect_result = await self.db.execute(defect_stmt)
        defect_counts = {r[0]: r[1] for r in defect_result.all()}

        # Open defects by severity
        severity_stmt = select(
            QualityDefect.severity, func.count(QualityDefect.defect_id)
        ).where(
            QualityDefect.project_id == project_id,
            QualityDefect.status == "open",
        ).group_by(QualityDefect.severity)
        severity_result = await self.db.execute(severity_stmt)
        severity_counts = {r[0]: r[1] for r in severity_result.all()}

        # Latest metrics
        metric_stmt = select(QualityMetric).where(
            QualityMetric.project_id == project_id
        ).order_by(QualityMetric.measurement_date.desc()).limit(10)
        metric_result = await self.db.execute(metric_stmt)
        metrics = metric_result.scalars().all()

        return {
            "projectId": project_id,
            "defectsByStatus": defect_counts,
            "openDefectsBySeverity": severity_counts,
            "latestMetrics": [
                {
                    "metricId": m.metric_id,
                    "metricName": m.metric_name,
                    "metricValue": float(m.metric_value) if m.metric_value else None,
                    "targetValue": float(m.target_value) if m.target_value else None,
                    "unit": m.unit,
                    "measurementDate": str(m.measurement_date) if m.measurement_date else None,
                }
                for m in metrics
            ],
        }

    # ── Internal helpers ────────────────────────────────────────────────

    async def _defect_or_404(self, defect_id: str) -> QualityDefect:
        defect = await self.db.get(QualityDefect, defect_id)
        if not defect:
            raise ResourceNotFoundError("QualityDefect", defect_id)
        return defect

    async def _metric_or_404(self, metric_id: str) -> QualityMetric:
        metric = await self.db.get(QualityMetric, metric_id)
        if not metric:
            raise ResourceNotFoundError("QualityMetric", metric_id)
        return metric
