"""API routes: upload, invoices, match, tax-assist."""

import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Invoice, PO, Receipt, Voucher
from app.schemas import InvoiceOut, MatchRequest, MatchResult, TaxAssistRequest, TaxReportOut

router = APIRouter()

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/health")
def api_health() -> dict:
    """API health check."""
    return {"status": "ok"}


@router.post("/upload-file")
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict:
    """Accept a file upload; save to disk."""
    ext = Path(file.filename or "").suffix or ".bin"
    name = f"{uuid.uuid4().hex}{ext}"
    path = UPLOAD_DIR / name
    try:
        with path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Save failed: {e}") from e
    return {"filename": file.filename, "saved_as": name, "path": str(path)}


@router.post("/upload-invoice", response_model=InvoiceOut)  # includes workflow_steps when present
def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> InvoiceOut:
    """Upload invoice (PDF/image), run OCR + LLM extraction, store in DB."""
    ext = Path(file.filename or "").suffix or ".bin"
    name = f"{uuid.uuid4().hex}{ext}"
    path = UPLOAD_DIR / name
    try:
        with path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Save failed: {e}") from e
    try:
        from app.agents import run_ocr_and_extract_with_trace, save_invoice_from_extraction

        raw_text, extracted_json, steps_log = run_ocr_and_extract_with_trace(str(path))
        inv = save_invoice_from_extraction(db, raw_text, extracted_json, file_path=str(path))
        return InvoiceOut(
            id=inv.id,
            date=inv.date.isoformat() if inv.date else None,
            amount=inv.amount,
            vendor=inv.vendor,
            raw_text=(inv.raw_text[:200] + "...") if inv.raw_text and len(inv.raw_text) > 200 else inv.raw_text,
            extracted_json=inv.extracted_json,
            file_path=inv.file_path,
            created_at=inv.created_at.isoformat(),
            workflow_steps=steps_log,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}") from e


@router.get("/invoices", response_model=list[InvoiceOut])
def list_invoices(db: Session = Depends(get_db)) -> list[InvoiceOut]:
    """List all invoices."""
    rows = db.query(Invoice).order_by(Invoice.created_at.desc()).all()
    return [
        InvoiceOut(
            id=r.id,
            date=r.date.isoformat() if r.date else None,
            amount=r.amount,
            vendor=r.vendor,
            raw_text=(r.raw_text[:200] + "...") if r.raw_text and len(r.raw_text) > 200 else r.raw_text,
            extracted_json=r.extracted_json,
            file_path=r.file_path,
            created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]


@router.post("/match", response_model=MatchResult)
def run_match(
    body: MatchRequest,
    db: Session = Depends(get_db),
) -> MatchResult:
    """Run three-way matching (delegated to MatchingAgent in agents.py)."""
    from app.agents import run_matching_agent

    return run_matching_agent(
        invoice_id=body.invoice_id,
        po_id=body.po_id,
        receipt_id=body.receipt_id,
        db=db,
    )


@router.post("/tax-assist", response_model=TaxReportOut)
def tax_assist(
    body: TaxAssistRequest,
    db: Session = Depends(get_db),
) -> TaxReportOut:
    """Generate tax report for an invoice (delegated to TaxAgent)."""
    from app.agents import run_tax_agent

    try:
        return run_tax_agent(invoice_id=body.invoice_id, db=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
