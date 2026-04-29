"""Quality module ORM models (2 tables)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class QualityDefect(Base):
    __tablename__ = "pm_quality_defect"

    defect_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    defect_name: Mapped[str] = mapped_column(String(200))
    defect_type: Mapped[str | None] = mapped_column(String(20))
    severity: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="open")
    found_by: Mapped[str | None] = mapped_column(String(64))
    assigned_to: Mapped[str | None] = mapped_column(String(64))
    found_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    fixed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class QualityMetric(Base):
    __tablename__ = "pm_quality_metric"

    metric_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    metric_name: Mapped[str] = mapped_column(String(100))
    metric_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    target_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    measurement_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(20))
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)
