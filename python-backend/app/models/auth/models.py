"""Auth module ORM models: User, LoginAttempt, and join tables."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.core.field_encryption import EncryptedFieldMixin


class User(EncryptedFieldMixin, TimestampMixin, Base):
    __tablename__ = "pm_sys_user"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str | None] = mapped_column(String(100))
    dept_id: Mapped[str | None] = mapped_column(String(64))
    email: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[int] = mapped_column(Integer, default=1)
    password_changed_at: Mapped[datetime | None] = mapped_column(nullable=True)


class LoginAttempt(Base):
    __tablename__ = "pm_login_attempt"

    attempt_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(64))
    username: Mapped[str | None] = mapped_column(String(50))
    ip_address: Mapped[str | None] = mapped_column(String(50))
    success: Mapped[int] = mapped_column(Integer, default=0)
    failure_reason: Mapped[str | None] = mapped_column(String(200))
    attempt_time: Mapped[datetime | None] = mapped_column(nullable=True)


class UserRole(Base):
    __tablename__ = "pm_sys_user_role"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    role_id: Mapped[str] = mapped_column(String(64), primary_key=True)


class RolePermission(Base):
    __tablename__ = "pm_sys_role_permission"

    role_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    permission_id: Mapped[str] = mapped_column(String(64), primary_key=True)
