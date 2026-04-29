"""SQLAlchemy Base model with common fields."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """Mixin that adds create_time and update_time columns."""

    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class UUIDPrimaryKeyMixin:
    """Mixin for VARCHAR(64) UUID primary keys."""

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
