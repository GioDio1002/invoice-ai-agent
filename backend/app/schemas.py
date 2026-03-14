"""Pydantic schemas for API request/response."""

from typing import Any

from pydantic import BaseModel, Field


class InvoiceOut(BaseModel):
    """Invoice list/detail response."""

    id: int
    date: str | None = None
    amount: float | None = None
    vendor: str | None = None
    raw_text: str | None = None
    extracted_json: dict[str, Any] | None = None
    file_path: str | None = None
    created_at: str


class MatchRequest(BaseModel):
    """Request body for three-way match."""

    invoice_id: int
    po_id: int | None = None
    receipt_id: int | None = None


class MatchResult(BaseModel):
    """Result of matching agent."""

    matched: bool
    message: str
    details: dict[str, Any] | None = None


class TaxAssistRequest(BaseModel):
    """Request body for tax-assist."""

    invoice_id: int


class TaxReportOut(BaseModel):
    """Tax report response."""

    id: int
    invoice_id: int
    summary: str | None = None
    vat_amount: float | None = None
    deductions: dict[str, Any] | None = None
    created_at: str
