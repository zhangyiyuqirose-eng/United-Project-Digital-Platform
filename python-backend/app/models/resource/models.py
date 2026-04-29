"""Resource pool module ORM models — company-owned staff placed at head office.

Covers: OutsourcePerson, PoolMembership, SkillProfile, AttendanceRecord,
Settlement, PoolPosition, PerformanceEval, PersonnelReplacement, LeaveRequest.
Per requirement spec 4.5 (F-501 ~ F-513).
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.core.field_encryption import EncryptedFieldMixin


# ---------------------------------------------------------------------------
# Individual staff members (F-501: 外包人员档案管理)
# ---------------------------------------------------------------------------
class OutsourcePerson(EncryptedFieldMixin, Base):
    __tablename__ = "pm_outsource_person"

    person_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    emp_code: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(50))
    id_card: Mapped[str] = mapped_column(String(200))  # encrypted SM4
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(100))
    skill_tags: Mapped[str | None] = mapped_column(Text)  # JSON array
    level: Mapped[int] = mapped_column(Integer)  # 1:初级 2:中级 3:高级 4:专家
    daily_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    department: Mapped[str | None] = mapped_column(String(100))
    pool_status: Mapped[int] = mapped_column(Integer, default=0)  # 0:可用 1:已分配 2:已退场
    current_project: Mapped[str | None] = mapped_column(String(64))
    entry_date: Mapped[date | None] = mapped_column(Date)
    exit_date: Mapped[date | None] = mapped_column(Date)
    background_check: Mapped[int | None] = mapped_column(Integer)  # 0:未审 1:通过 2:不通过
    security_review: Mapped[int | None] = mapped_column(Integer)
    confidentiality_agreement: Mapped[int | None] = mapped_column(Integer)
    attendance_group: Mapped[str | None] = mapped_column(String(64))
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)
    update_time: Mapped[datetime | None] = mapped_column(nullable=True)


# ---------------------------------------------------------------------------
# Pool membership tracking (F-504/F-511: 入池/出池)
# ---------------------------------------------------------------------------
class PoolMembership(Base):
    __tablename__ = "pm_pool_membership"

    membership_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    person_id: Mapped[str] = mapped_column(String(64))
    pool_id: Mapped[str] = mapped_column(String(64))
    status: Mapped[int] = mapped_column(Integer, default=0)  # 0:待入池 1:在池 2:已出池 3:暂停
    entry_date: Mapped[date | None] = mapped_column(Date)
    exit_date: Mapped[date | None] = mapped_column(Date)
    approved_by: Mapped[str | None] = mapped_column(String(64))
    approval_date: Mapped[datetime | None] = mapped_column(DateTime)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)
    update_time: Mapped[datetime | None] = mapped_column(nullable=True)


# ---------------------------------------------------------------------------
# Skill profiles (F-502: 技能图谱与标签体系)
# ---------------------------------------------------------------------------
class SkillProfile(Base):
    __tablename__ = "pm_skill_profile"

    skill_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    person_id: Mapped[str] = mapped_column(String(64))
    skill_name: Mapped[str] = mapped_column(String(50))
    proficiency: Mapped[int] = mapped_column(Integer)  # 1:入门 2:熟练 3:精通
    cert_name: Mapped[str | None] = mapped_column(String(100))
    cert_date: Mapped[date | None] = mapped_column(Date)
    expiry_date: Mapped[date | None] = mapped_column(Date)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)
    update_time: Mapped[datetime | None] = mapped_column(nullable=True)


# ---------------------------------------------------------------------------
# Attendance records (F-506: 驻场考勤核验)
# ---------------------------------------------------------------------------
class AttendanceRecord(Base):
    __tablename__ = "pm_attendance_record"

    attendance_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    person_id: Mapped[str] = mapped_column(String(64))
    date: Mapped[date] = mapped_column(Date)
    check_in_time: Mapped[datetime | None] = mapped_column(DateTime)
    check_out_time: Mapped[datetime | None] = mapped_column(DateTime)
    gps_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    gps_lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    wifi_mac: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[int] = mapped_column(Integer, default=0)  # 0:正常 1:迟到 2:早退 3:缺勤 4:外勤
    project_id: Mapped[str | None] = mapped_column(String(64))
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)
    update_time: Mapped[datetime | None] = mapped_column(nullable=True)


# ---------------------------------------------------------------------------
# Monthly settlement (F-508/F-509: 费用结算 / 账单生成)
# ---------------------------------------------------------------------------
class Settlement(Base):
    __tablename__ = "pm_settlement"

    settlement_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    person_id: Mapped[str] = mapped_column(String(64))
    period: Mapped[str] = mapped_column(String(20))  # "2026-04"
    valid_hours: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    standard_hours: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    daily_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    performance_coeff: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), default=1.0)
    overtime_hours: Mapped[Decimal | None] = mapped_column(Numeric(5, 1))
    overtime_fee: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), default=0)
    total_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    status: Mapped[int] = mapped_column(Integer, default=0)  # 0:草稿 1:待确认 2:已确认 3:已开票
    confirmed_by: Mapped[str | None] = mapped_column(String(64))
    confirmed_date: Mapped[datetime | None] = mapped_column(DateTime)
    invoice_date: Mapped[date | None] = mapped_column(Date)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)
    update_time: Mapped[datetime | None] = mapped_column(nullable=True)


# ---------------------------------------------------------------------------
# Pool positions (F-503: 资源池岗位管理)
# ---------------------------------------------------------------------------
class PoolPosition(Base):
    __tablename__ = "pm_pool_position"

    position_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(64))
    position_name: Mapped[str] = mapped_column(String(100))
    level: Mapped[int] = mapped_column(Integer)
    skill_requirements: Mapped[str | None] = mapped_column(Text)  # JSON
    head_count: Mapped[int] = mapped_column(Integer, default=1)
    filled_count: Mapped[int] = mapped_column(Integer, default=0)
    department: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[int] = mapped_column(Integer, default=1)  # 0:关闭 1:开放
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)
    update_time: Mapped[datetime | None] = mapped_column(nullable=True)


# ---------------------------------------------------------------------------
# Performance evaluation — 5-dimension (F-510: 绩效评价)
# ---------------------------------------------------------------------------
class PerformanceEval(Base):
    __tablename__ = "pm_performance_eval"

    eval_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    person_id: Mapped[str] = mapped_column(String(64))
    project_id: Mapped[str | None] = mapped_column(String(64))
    period: Mapped[str | None] = mapped_column(String(20))
    # 5 weighted dimensions
    pm_satisfaction: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))  # 40%
    timesheet_compliance: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))  # 20%
    task_completion: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))  # 20%
    quality_metric: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))  # 10%
    attendance_compliance: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))  # 10%
    # Computed
    overall_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    grade: Mapped[str | None] = mapped_column(String(1))  # A/B/C/D
    evaluator_id: Mapped[str | None] = mapped_column(String(64))
    comments: Mapped[str | None] = mapped_column(Text)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)
    update_time: Mapped[datetime | None] = mapped_column(nullable=True)


# ---------------------------------------------------------------------------
# Legacy tables (kept for backward compatibility)
# ---------------------------------------------------------------------------
class ResourcePool(Base):
    """Pool container (multiple people belong to one pool via PoolMembership)."""
    __tablename__ = "pm_resource_pool"

    pool_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    pool_name: Mapped[str] = mapped_column(String(100))
    manager_id: Mapped[str | None] = mapped_column(String(64))
    description: Mapped[str | None] = mapped_column(String(500))
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class LeaveRequest(Base):
    __tablename__ = "pm_leave_request"

    leave_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    person_id: Mapped[str] = mapped_column(String(64))
    leave_type: Mapped[str | None] = mapped_column(String(20))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    days: Mapped[int | None] = mapped_column(Integer)
    reason: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    approver_id: Mapped[str | None] = mapped_column(String(64))
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class PersonnelReplacement(Base):
    __tablename__ = "pm_personnel_replacement"

    replace_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    person_id: Mapped[str] = mapped_column(String(64))
    project_id: Mapped[str] = mapped_column(String(64))
    reason: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)
