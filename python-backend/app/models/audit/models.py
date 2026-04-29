"""Audit module ORM models (1 table)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditLogEntry(Base):
    __tablename__ = "pm_audit_log_entry"

    entry_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    audit_id: Mapped[str | None] = mapped_column(String(64))
    user_id: Mapped[str | None] = mapped_column(String(64))
    action: Mapped[str | None] = mapped_column(String(50))
    resource_type: Mapped[str | None] = mapped_column(String(50))
    resource_id: Mapped[str | None] = mapped_column(String(64))
    details: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(String(50))
    timestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
