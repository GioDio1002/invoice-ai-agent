"""SQLAlchemy models for invoices, vouchers, POs, receipts, tax reports."""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base for all models."""

    pass


class Invoice(Base):
    """Extracted invoice data from OCR + LLM."""

    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    vendor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    vouchers = relationship("Voucher", back_populates="invoice")
    tax_reports = relationship("TaxReport", back_populates="invoice")


class Voucher(Base):
    """Accounting voucher generated from an invoice."""

    __tablename__ = "vouchers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    entry_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    invoice = relationship("Invoice", back_populates="vouchers")


class PO(Base):
    """Purchase order (user-uploaded or stored)."""

    __tablename__ = "pos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Receipt(Base):
    """Receipt / goods received (user-uploaded or stored)."""

    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TaxReport(Base):
    """Tax report/summary for an invoice."""

    __tablename__ = "tax_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    vat_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    deductions: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    invoice = relationship("Invoice", back_populates="tax_reports")
