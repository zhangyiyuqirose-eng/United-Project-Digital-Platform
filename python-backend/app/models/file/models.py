"""File module ORM models (1 table)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FileInfo(Base):
    __tablename__ = "pm_file_info"

    file_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    file_name: Mapped[str] = mapped_column(String(200))
    file_path: Mapped[str | None] = mapped_column(String(500))
    file_type: Mapped[str | None] = mapped_column(String(50))
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    project_id: Mapped[str | None] = mapped_column(String(64))
    uploader_id: Mapped[str | None] = mapped_column(String(64))
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)
