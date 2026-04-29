"""Notify module ORM models (3 tables)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class NotifyMessage(Base):
    __tablename__ = "pm_notify_message"

    message_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str | None] = mapped_column(Text)
    type: Mapped[str | None] = mapped_column(String(20))
    sender_id: Mapped[str | None] = mapped_column(String(64))
    receiver_id: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20), default="unread")
    send_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    read_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class NotifyTemplate(Base):
    __tablename__ = "pm_notify_template"

    template_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    template_name: Mapped[str] = mapped_column(String(100))
    template_code: Mapped[str | None] = mapped_column(String(50), unique=True)
    template_content: Mapped[str | None] = mapped_column(Text)
    type: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="active")
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class NotifyPreference(Base):
    __tablename__ = "pm_notify_preference"

    pref_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64))
    notify_type: Mapped[str | None] = mapped_column(String(20))
    enabled: Mapped[int] = mapped_column(Integer, default=1)
    channel: Mapped[str | None] = mapped_column(String(20))
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)
