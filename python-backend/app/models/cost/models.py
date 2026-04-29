"""Cost module ORM models (5 tables)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DateTime, Date, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Budget(TimestampMixin, Base):
    __tablename__ = "pm_budget"

    budget_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    budget_year: Mapped[int | None] = mapped_column(Integer)
    total_budget: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    labor_budget: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    outsource_budget: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    procurement_budget: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    other_budget: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(64))
    approved_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT")


class Cost(Base):
    __tablename__ = "pm_cost"

    cost_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    cost_type: Mapped[str] = mapped_column(String(20))
    amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    calculate_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    evm_pv: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    evm_ev: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    evm_ac: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class CostAlert(Base):
    __tablename__ = "pm_cost_alert"

    alert_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    budget_id: Mapped[str | None] = mapped_column(String(64))
    alert_type: Mapped[str | None] = mapped_column(String(20))
    threshold: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    current_value: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    message: Mapped[str | None] = mapped_column(Text)
    is_handled: Mapped[int] = mapped_column(Integer, default=0)
    severity: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    created_by: Mapped[str | None] = mapped_column(String(64))
    ack_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolve_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class CostOutsource(Base):
    __tablename__ = "pm_cost_outsource"

    outsource_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    vendor_name: Mapped[str | None] = mapped_column(String(200))
    contract_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    paid_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class ExpenseReimbursement(Base):
    __tablename__ = "pm_expense_reimbursement"

    expense_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64))
    project_id: Mapped[str | None] = mapped_column(String(64))
    expense_type: Mapped[str | None] = mapped_column(String(20))
    amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    apply_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text)
    attachments: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    approver_id: Mapped[str | None] = mapped_column(String(64))
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class CostSettlement(TimestampMixin, Base):
    __tablename__ = "pm_cost_settlement"

    settlement_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    settlement_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    settlement_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_by: Mapped[str | None] = mapped_column(String(64))
