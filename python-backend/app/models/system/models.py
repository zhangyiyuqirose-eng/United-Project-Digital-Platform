"""System module ORM models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Dept(TimestampMixin, Base):
    __tablename__ = "pm_sys_dept"

    dept_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dept_name: Mapped[str] = mapped_column(String(100))
    parent_id: Mapped[str | None] = mapped_column(String(64))
    leader_id: Mapped[str | None] = mapped_column(String(64))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1)


class Role(TimestampMixin, Base):
    __tablename__ = "pm_sys_role"

    role_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    role_name: Mapped[str] = mapped_column(String(50))
    role_code: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(String(200))
    data_scope: Mapped[str] = mapped_column(String(20), default="all")
    status: Mapped[int] = mapped_column(Integer, default=1)


class Permission(Base):
    __tablename__ = "pm_sys_permission"

    permission_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    permission_name: Mapped[str] = mapped_column(String(50))
    permission_code: Mapped[str] = mapped_column(String(100), unique=True)
    resource_type: Mapped[str | None] = mapped_column(String(20))
    resource_url: Mapped[str | None] = mapped_column(String(200))
    parent_id: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[int] = mapped_column(Integer, default=1)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class Dict(Base):
    __tablename__ = "pm_sys_dict"

    dict_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dict_type: Mapped[str] = mapped_column(String(50))
    dict_label: Mapped[str] = mapped_column(String(100))
    dict_value: Mapped[str] = mapped_column(String(100))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class Config(TimestampMixin, Base):
    __tablename__ = "pm_sys_config"

    config_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    config_key: Mapped[str] = mapped_column(String(100), unique=True)
    config_value: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(String(200))


class Announcement(Base):
    __tablename__ = "pm_sys_announcement"

    announcement_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str | None] = mapped_column(Text)
    type: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[int] = mapped_column(Integer, default=1)
    publisher_id: Mapped[str | None] = mapped_column(String(64))
    publish_time: Mapped[datetime | None] = mapped_column(nullable=True)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class AuditLog(Base):
    __tablename__ = "pm_sys_audit_log"

    log_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(64))
    operation: Mapped[str | None] = mapped_column(String(50))
    method: Mapped[str | None] = mapped_column(String(100))
    params: Mapped[str | None] = mapped_column(Text)
    ip: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[int | None] = mapped_column(Integer)
    error_msg: Mapped[str | None] = mapped_column(Text)
    execute_time: Mapped[int | None] = mapped_column(Integer)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class Meeting(Base):
    __tablename__ = "pm_meeting"

    meeting_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    meeting_name: Mapped[str] = mapped_column(String(200))
    meeting_type: Mapped[str | None] = mapped_column(String(20))
    start_time: Mapped[datetime | None] = mapped_column(nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(nullable=True)
    location: Mapped[str | None] = mapped_column(String(200))
    organizer_id: Mapped[str | None] = mapped_column(String(64))
    participants: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(String(20))
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class ReviewMeeting(Base):
    __tablename__ = "pm_review_meeting"

    review_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str | None] = mapped_column(String(64))
    review_type: Mapped[str | None] = mapped_column(String(20))
    review_date: Mapped[datetime | None] = mapped_column(nullable=True)
    reviewer_id: Mapped[str | None] = mapped_column(String(64))
    conclusion: Mapped[str | None] = mapped_column(String(200))
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class ReviewOpinion(Base):
    __tablename__ = "pm_review_opinion"

    opinion_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    review_id: Mapped[str | None] = mapped_column(String(64))
    reviewer_id: Mapped[str | None] = mapped_column(String(64))
    opinion_type: Mapped[str | None] = mapped_column(String(20))
    opinion_content: Mapped[str | None] = mapped_column(Text)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class Asset(Base):
    __tablename__ = "pm_asset"

    asset_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    asset_name: Mapped[str] = mapped_column(String(200))
    asset_type: Mapped[str | None] = mapped_column(String(20))
    asset_code: Mapped[str | None] = mapped_column(String(50), unique=True)
    owner_id: Mapped[str | None] = mapped_column(String(64))
    location: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str | None] = mapped_column(String(20))
    purchase_date: Mapped[datetime | None] = mapped_column(nullable=True)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)
