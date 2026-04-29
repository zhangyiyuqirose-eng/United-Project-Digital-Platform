"""Workflow module ORM models."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProcessDefinition(Base):
    __tablename__ = "pm_process_definition"

    def_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    process_key: Mapped[str] = mapped_column(String(100), unique=True)
    process_name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str | None] = mapped_column(String(50))
    deployment_id: Mapped[str | None] = mapped_column(String(100))
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="active")
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class ProcessInstance(Base):
    __tablename__ = "pm_process_instance"

    instance_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    process_def_id: Mapped[str] = mapped_column(String(64))
    process_key: Mapped[str] = mapped_column(String(100))
    business_key: Mapped[str | None] = mapped_column(String(100))
    submitter_id: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    current_step: Mapped[str | None] = mapped_column(String(100))
    variables: Mapped[str | None] = mapped_column(Text)
    create_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    update_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    complete_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
