"""Business module ORM models (7 tables)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Contract(Base):
    __tablename__ = "pm_contract"

    contract_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    contract_code: Mapped[str | None] = mapped_column(String(50), unique=True)
    contract_name: Mapped[str] = mapped_column(String(200))
    contract_type: Mapped[str | None] = mapped_column(String(20))
    party_a: Mapped[str | None] = mapped_column(String(200))
    party_b: Mapped[str | None] = mapped_column(String(200))
    total_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10))
    sign_date: Mapped[str | None] = mapped_column(String(20))
    start_date: Mapped[str | None] = mapped_column(String(20))
    end_date: Mapped[str | None] = mapped_column(String(20))
    project_id: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_by: Mapped[str | None] = mapped_column(String(64))
    create_time: Mapped[str | None] = mapped_column(String(30))
    update_time: Mapped[str | None] = mapped_column(String(30))
    reminder_days: Mapped[int | None] = mapped_column(Integer)


class ContractPayment(Base):
    __tablename__ = "pm_contract_payment"

    payment_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    contract_id: Mapped[str] = mapped_column(String(64))
    payment_type: Mapped[str | None] = mapped_column(String(20))
    planned_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    actual_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    planned_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class Customer(TimestampMixin, Base):
    __tablename__ = "pm_customer"

    customer_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(200))
    customer_type: Mapped[str | None] = mapped_column(String(20))
    contact_person: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(String(500))
    industry: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="active")


class Supplier(TimestampMixin, Base):
    __tablename__ = "pm_supplier"

    supplier_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    supplier_name: Mapped[str] = mapped_column(String(200))
    supplier_type: Mapped[str | None] = mapped_column(String(20))
    contact_person: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="active")


class Opportunity(Base):
    __tablename__ = "pm_business_opportunity"

    opportunity_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    opportunity_name: Mapped[str] = mapped_column(String(200))
    customer_id: Mapped[str | None] = mapped_column(String(64))
    expected_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    probability: Mapped[int | None] = mapped_column(Integer)
    stage: Mapped[str | None] = mapped_column(String(20))
    owner_id: Mapped[str | None] = mapped_column(String(64))
    expected_close_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open")
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class Quotation(Base):
    __tablename__ = "pm_quotation"

    quotation_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    opportunity_id: Mapped[str | None] = mapped_column(String(64))
    customer_id: Mapped[str | None] = mapped_column(String(64))
    quotation_no: Mapped[str | None] = mapped_column(String(50))
    amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class ProcurementPlan(Base):
    __tablename__ = "pm_procurement_plan"

    plan_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64))
    plan_name: Mapped[str] = mapped_column(String(200))
    procurement_type: Mapped[str | None] = mapped_column(String(20))
    budget: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    planned_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)


class ContractInvoice(Base):
    __tablename__ = "pm_contract_invoice"

    invoice_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    contract_id: Mapped[str] = mapped_column(String(64))
    invoice_no: Mapped[str] = mapped_column(String(50))
    invoice_type: Mapped[str | None] = mapped_column(String(20))
    amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    create_time: Mapped[datetime | None] = mapped_column(nullable=True)
