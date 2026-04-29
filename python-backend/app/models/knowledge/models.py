"""Knowledge module ORM models (4 tables)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class KnowledgeDoc(TimestampMixin, Base):
    __tablename__ = "pm_knowledge_doc"

    doc_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    doc_type: Mapped[str | None] = mapped_column(String(20))
    template_type: Mapped[str | None] = mapped_column(String(20))
    category: Mapped[str | None] = mapped_column(String(100))
    content: Mapped[str | None] = mapped_column(Text)
    author_id: Mapped[str | None] = mapped_column(String(64))
    created_by: Mapped[str | None] = mapped_column(String(64))
    version: Mapped[str | None] = mapped_column(String(20))
    version_num: Mapped[int | None] = mapped_column(Integer)
    file_path: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="draft")
    publish_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class KnowledgeTemplate(Base):
    __tablename__ = "pm_knowledge_template"

    template_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    template_name: Mapped[str] = mapped_column(String(200))
    template_type: Mapped[str | None] = mapped_column(String(20))
    content: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active")
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class KnowledgeReview(Base):
    __tablename__ = "pm_knowledge_review"

    review_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    doc_id: Mapped[str] = mapped_column(String(64))
    reviewer_id: Mapped[str | None] = mapped_column(String(64))
    review_status: Mapped[str | None] = mapped_column(String(20))
    comments: Mapped[str | None] = mapped_column(Text)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class ComplianceChecklist(Base):
    __tablename__ = "pm_compliance_checklist"

    checklist_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    checklist_name: Mapped[str] = mapped_column(String(200))
    checklist_type: Mapped[str | None] = mapped_column(String(20))
    items: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class DocumentVersion(TimestampMixin, Base):
    __tablename__ = "pm_document_version"

    version_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    doc_id: Mapped[str] = mapped_column(String(64))
    version: Mapped[str | None] = mapped_column(String(20))
    version_num: Mapped[int | None] = mapped_column(Integer)
    content: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(String(64))


class Policy(TimestampMixin, Base):
    __tablename__ = "pm_policy"

    policy_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    policy_type: Mapped[str | None] = mapped_column(String(20))
    content: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="draft")
