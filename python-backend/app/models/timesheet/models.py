"""Timesheet module ORM models (2 tables)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Timesheet(TimestampMixin, Base):
    __tablename__ = "pm_timesheet"

    timesheet_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    staff_id: Mapped[str] = mapped_column(String(64))
    project_id: Mapped[str] = mapped_column(String(64))
    work_date: Mapped[date | None] = mapped_column(Date)
    hours: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    check_status: Mapped[str] = mapped_column(String(20), default="pending")
    attendance_check_result: Mapped[str | None] = mapped_column(String(200))
    remark: Mapped[str | None] = mapped_column(Text)


class TimesheetAttendance(Base):
    __tablename__ = "pm_timesheet_attendance"

    attendance_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64))
    date: Mapped[date | None] = mapped_column(Date)
    check_in_time: Mapped[datetime | None] = mapped_column(nullable=True)
    check_out_time: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str | None] = mapped_column(String(20))
    project_id: Mapped[str | None] = mapped_column(String(64))
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)
