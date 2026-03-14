"""LangChain agents: extraction, matching, tax."""

import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.llm_client import get_llm, parse_invoice_with_llm
from app.models import Invoice, PO, Receipt, TaxReport
from app.ocr import extract_text_from_file
from app.rag import add_documents_to_rag, get_retriever
from app.schemas import MatchResult, TaxReportOut


def run_ocr_and_extract(file_path: str) -> tuple[str, dict[str, Any]]:
    """Run OCR on file, then LLM extraction. Returns (raw_text, extracted_json)."""
    from pathlib import Path
    raw_text = extract_text_from_file(Path(file_path))
    extracted = parse_invoice_with_llm(raw_text)
    return raw_text, extracted


def save_invoice_from_extraction(
    db: Session,
    raw_text: str,
    extracted_json: dict[str, Any],
    file_path: str | None = None,
) -> Invoice:
    """Create and persist Invoice from extracted data."""
    inv = Invoice(
        raw_text=raw_text or None,
        extracted_json=extracted_json or None,
        file_path=file_path,
    )
    if extracted_json:
        if isinstance(extracted_json.get("date"), str):
            try:
                inv.date = datetime.fromisoformat(extracted_json["date"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass
        inv.amount = extracted_json.get("amount")
        if isinstance(inv.amount, (int, float)):
            inv.amount = float(inv.amount)
        else:
            inv.amount = None
        inv.vendor = extracted_json.get("vendor") if isinstance(extracted_json.get("vendor"), str) else None
    db.add(inv)
    db.commit()
    db.refresh(inv)
    try:
        text_for_rag = (raw_text or "")[:8000] or json.dumps(extracted_json or {})
        add_documents_to_rag([text_for_rag], [{"invoice_id": inv.id, "vendor": inv.vendor}])
    except Exception:
        pass
    return inv


def _gather_match_context(
    db: Session,
    invoice_id: int,
    po_id: int | None,
    receipt_id: int | None,
) -> str:
    """Gather invoice, PO, receipt data and optional RAG context for matching."""
    parts = []
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        return ""
    parts.append("INVOICE (id=%s): %s" % (invoice_id, json.dumps(inv.extracted_json or {"raw": (inv.raw_text or "")[:500]})))
    if po_id:
        po = db.query(PO).filter(PO.id == po_id).first()
        if po:
            parts.append("PO (id=%s): %s" % (po_id, json.dumps(po.details or {})))
    if receipt_id:
        rec = db.query(Receipt).filter(Receipt.id == receipt_id).first()
        if rec:
            parts.append("RECEIPT (id=%s): %s" % (receipt_id, json.dumps(rec.details or {})))
    try:
        retriever = get_retriever(k=3)
        docs = retriever.invoke("invoice purchase order receipt matching")
        if docs:
            parts.append("Similar past documents:\n" + "\n---\n".join(d.page_content[:500] for d in docs))
    except Exception:
        pass
    return "\n\n".join(parts)


def run_matching_agent(
    invoice_id: int,
    po_id: int | None,
    receipt_id: int | None,
    db: Session,
) -> MatchResult:
    """Run three-way matching: compare invoice vs PO vs receipt; flag mismatches."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        return MatchResult(matched=False, message="Invoice not found", details=None)
    context = _gather_match_context(db, invoice_id, po_id, receipt_id)
    prompt = """You are a matching agent. Compare the invoice with the PO and receipt (if provided).
Respond with valid JSON only: {"matched": true/false, "message": "short summary", "mismatches": ["list of issues"]}.
If PO or receipt is missing, say so in message and set matched to false.
Context:
"""
    prompt += context[:8000]
    try:
        llm = get_llm()
        response = llm.invoke(prompt)
        text = response.content if hasattr(response, "content") else str(response)
        text = text.strip()
        if "```" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                text = text[start:end]
        data = json.loads(text)
        return MatchResult(
            matched=bool(data.get("matched", False)),
            message=data.get("message", "Match completed."),
            details={"mismatches": data.get("mismatches", []), "invoice_id": invoice_id, "po_id": po_id, "receipt_id": receipt_id},
        )
    except Exception as e:
        return MatchResult(
            matched=False,
            message="Matching failed: %s" % str(e),
            details={"invoice_id": invoice_id, "po_id": po_id, "receipt_id": receipt_id},
        )


def run_tax_agent(invoice_id: int, db: Session) -> TaxReportOut:
    """Generate tax report: VAT (assume 10%), deductions, filing suggestions."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise ValueError("Invoice not found")
    context = json.dumps(invoice.extracted_json or {"raw": (invoice.raw_text or "")[:2000]})
    try:
        retriever = get_retriever(k=2)
        docs = retriever.invoke("tax VAT deduction invoice")
        if docs:
            context += "\n\nSimilar docs: " + "\n".join(d.page_content[:300] for d in docs)
    except Exception:
        pass
    prompt = """You are a tax assistant. For this invoice, provide:
1) VAT at 10% on the total amount.
2) Short summary of tax relevance.
3) Suggested deductions (list).
4) Filing suggestion (e.g. quarterly VAT).
Respond with valid JSON only: {"summary": "...", "vat_amount": number, "deductions": ["..."], "filing_suggestion": "..."}
Invoice data:
"""
    prompt += context[:6000]
    vat_rate = 0.10
    vat_amount = float(invoice.amount * vat_rate) if invoice.amount else None
    summary = None
    deductions = None
    try:
        llm = get_llm()
        response = llm.invoke(prompt)
        text = response.content if hasattr(response, "content") else str(response)
        text = text.strip()
        if "```" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                text = text[start:end]
        data = json.loads(text)
        summary = data.get("summary") or ""
        if data.get("filing_suggestion"):
            summary += " Filing: " + str(data["filing_suggestion"])
        vat_amount = data.get("vat_amount") if isinstance(data.get("vat_amount"), (int, float)) else vat_amount
        deductions = data.get("deductions") if isinstance(data.get("deductions"), list) else None
    except Exception:
        summary = "Tax report generated; VAT at 10%."
    report = TaxReport(
        invoice_id=invoice_id,
        summary=summary,
        vat_amount=vat_amount,
        deductions=deductions,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return TaxReportOut(
        id=report.id,
        invoice_id=report.invoice_id,
        summary=report.summary,
        vat_amount=report.vat_amount,
        deductions=report.deductions,
        created_at=report.created_at.isoformat(),
    )
