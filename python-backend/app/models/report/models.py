"""Report module ORM models."""

from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ReportHistory(TimestampMixin, Base):
    __tablename__ = "pm_report_history"

    report_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    report_type: Mapped[str] = mapped_column(String(50))
    target_id: Mapped[str | None] = mapped_column(String(64))
    file_name: Mapped[str] = mapped_column(String(200))
    file_size: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="generated")
    created_by: Mapped[str | None] = mapped_column(String(64))
    error_message: Mapped[str | None] = mapped_column(Text)
