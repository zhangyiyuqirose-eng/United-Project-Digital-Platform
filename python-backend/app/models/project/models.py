"""Project module ORM models (13 tables)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DateTime, Date, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Project(TimestampMixin, Base):
    __tablename__ = "pm_project"

    project_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_name: Mapped[str] = mapped_column(String(200))
    project_code: Mapped[str | None] = mapped_column(String(50), unique=True)
    project_type: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="draft")
    manager_id: Mapped[str | None] = mapped_column(String(64))
    manager_name: Mapped[str | None] = mapped_column(String(100))
    department_id: Mapped[str | None] = mapped_column(String(64))
    department_name: Mapped[str | None] = mapped_column(String(100))
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    budget: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    customer: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    wbs_json: Mapped[str | None] = mapped_column(Text)
    milestone_json: Mapped[str | None] = mapped_column(Text)
    evm_pv: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    evm_ev: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    evm_ac: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    evm_cpi: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    evm_spi: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    health_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    init_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actual_end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    create_user: Mapped[str | None] = mapped_column(String(64))


class ProjectTask(TimestampMixin, Base):
    __tablename__ = "pm_project_task"

    task_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    task_name: Mapped[str] = mapped_column(String(200))
    assignee_id: Mapped[str | None] = mapped_column(String(64))
    assignee_name: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    wbs_id: Mapped[str | None] = mapped_column(String(64))
    parent_task_id: Mapped[str | None] = mapped_column(String(64))


class WbsNode(Base):
    __tablename__ = "pm_wbs_node"

    wbs_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(200))
    code: Mapped[str | None] = mapped_column(String(50))
    parent_id: Mapped[str | None] = mapped_column(String(64))
    level: Mapped[int | None] = mapped_column(Integer)
    sort_order: Mapped[int | None] = mapped_column(Integer)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class ProjectRisk(TimestampMixin, Base):
    __tablename__ = "pm_project_risk"

    risk_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    risk_code: Mapped[str | None] = mapped_column(String(32))
    risk_name: Mapped[str] = mapped_column(String(200))
    title: Mapped[str | None] = mapped_column(String(200))
    risk_type: Mapped[str | None] = mapped_column(String(20))
    category: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    probability: Mapped[int | None] = mapped_column(Integer)
    impact: Mapped[int | None] = mapped_column(Integer)
    level: Mapped[str | None] = mapped_column(String(20))
    severity: Mapped[str | None] = mapped_column(String(20))
    risk_score: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open")
    mitigation: Mapped[str | None] = mapped_column(Text)
    mitigation_plan: Mapped[str | None] = mapped_column(Text)
    contingency_plan: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[str | None] = mapped_column(String(64))
    owner_name: Mapped[str | None] = mapped_column(String(100))
    owner: Mapped[str | None] = mapped_column(String(64))
    identified_by: Mapped[str | None] = mapped_column(String(64))
    identified_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ProjectMilestone(Base):
    __tablename__ = "pm_project_milestone"

    milestone_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    milestone_name: Mapped[str] = mapped_column(String(200))
    planned_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class ProjectChange(Base):
    __tablename__ = "pm_project_change"

    change_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    change_type: Mapped[str | None] = mapped_column(String(20))
    change_reason: Mapped[str | None] = mapped_column(Text)
    impact_analysis: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    approver_id: Mapped[str | None] = mapped_column(String(64))
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class ProjectClose(Base):
    __tablename__ = "pm_project_close"

    close_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    close_type: Mapped[str | None] = mapped_column(String(20))
    close_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text)
    lessons_learned: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class Sprint(Base):
    __tablename__ = "pm_sprint"

    sprint_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    sprint_name: Mapped[str] = mapped_column(String(100))
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="planning")
    goal: Mapped[str | None] = mapped_column(Text)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class PreInitiation(Base):
    __tablename__ = "pm_pre_initiation"

    pre_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    feasibility_study: Mapped[str | None] = mapped_column(Text)
    business_case: Mapped[str | None] = mapped_column(Text)
    initial_budget: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    expected_roi: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class ProgressAlert(Base):
    __tablename__ = "pm_progress_alert"

    alert_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    task_id: Mapped[str | None] = mapped_column(String(64))
    alert_type: Mapped[str | None] = mapped_column(String(20))
    alert_level: Mapped[str | None] = mapped_column(String(20))
    message: Mapped[str | None] = mapped_column(Text)
    is_handled: Mapped[int] = mapped_column(Integer, default=0)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class CodeRepo(Base):
    __tablename__ = "pm_code_repo"

    repo_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    repo_name: Mapped[str] = mapped_column(String(200))
    repo_url: Mapped[str | None] = mapped_column(String(500))
    branch: Mapped[str | None] = mapped_column(String(100))
    last_commit: Mapped[str | None] = mapped_column(String(100))
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class BuildRecord(Base):
    __tablename__ = "pm_build_record"

    build_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    build_number: Mapped[str | None] = mapped_column(String(50))
    build_status: Mapped[str | None] = mapped_column(String(20))
    build_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration: Mapped[int | None] = mapped_column(Integer)
    log_url: Mapped[str | None] = mapped_column(String(500))
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class ProjectDependency(Base):
    __tablename__ = "pm_project_dependency"

    dep_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    depends_on_project_id: Mapped[str] = mapped_column(String(64))
    dependency_type: Mapped[str | None] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(Text)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)
