"""LangGraph agentic workflow: invoice ingest → OCR → extract → validate (with optional LLM retry)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any, Literal, TypedDict

from langgraph.graph import END, StateGraph

from app.llm_client import get_llm, parse_invoice_with_llm
from app.ocr import extract_text_from_file


def _append_log(existing: list[str], new: list[str]) -> list[str]:
    return (existing or []) + (new or [])


class InvoicePipelineState(TypedDict, total=False):
    """State flowing through the invoice ingestion graph."""

    file_path: str
    raw_text: str
    extracted_json: dict[str, Any]
    validation_ok: bool
    retry_count: int
    error: str | None
    steps_log: Annotated[list[str], _append_log]


def node_ingest(state: InvoicePipelineState) -> dict[str, Any]:
    path = state.get("file_path") or ""
    if not path or not Path(path).is_file():
        return {
            "error": "Invalid or missing file_path",
            "steps_log": ["ingest: failed (no file)"],
        }
    return {"steps_log": ["ingest: file ready"], "error": None}


def node_ocr(state: InvoicePipelineState) -> dict[str, Any]:
    if state.get("error"):
        return {}
    try:
        path = Path(state["file_path"])
        raw = extract_text_from_file(path)
        return {
            "raw_text": raw or "",
            "steps_log": ["ocr: text extracted (%d chars)" % len(raw or "")],
        }
    except Exception as e:
        return {"error": "OCR failed: %s" % e, "steps_log": ["ocr: error"]}


def node_extract(state: InvoicePipelineState) -> dict[str, Any]:
    if state.get("error"):
        return {}
    raw = state.get("raw_text") or ""
    try:
        extracted = parse_invoice_with_llm(raw)
        return {
            "extracted_json": extracted,
            "steps_log": ["extract: LLM structured fields"],
        }
    except Exception as e:
        return {
            "extracted_json": {
                "date": None,
                "amount": None,
                "vendor": None,
                "items": [],
                "_error": str(e),
            },
            "steps_log": ["extract: fallback empty"],
        }


def node_validate(state: InvoicePipelineState) -> dict[str, Any]:
    if state.get("error"):
        return {"validation_ok": False}
    data = state.get("extracted_json") or {}
    ok = isinstance(data, dict) and (
        data.get("vendor") is not None
        or data.get("amount") is not None
        or (state.get("raw_text") or "").strip()
    )
    retry = int(state.get("retry_count") or 0)
    logs = ["validate: %s" % ("ok" if ok else "weak")]
    if not ok and retry < 1 and (state.get("raw_text") or "").strip():
        try:
            llm = get_llm()
            prompt = (
                "From this invoice text, output ONLY valid JSON: "
                '{"date":"YYYY-MM-DD or null","amount":number or null,'
                '"vendor":"string or null","items":[]}\n'
            )
            prompt += (state.get("raw_text") or "")[:10000]
            r = llm.invoke(prompt)
            text = (r.content if hasattr(r, "content") else str(r) or "").strip()
            if "```" in text:
                i, j = text.find("{"), text.rfind("}") + 1
                if i >= 0 and j > i:
                    text = text[i:j]
            repaired = json.loads(text)
            return {
                "extracted_json": repaired,
                "validation_ok": True,
                "retry_count": retry + 1,
                "steps_log": logs + ["validate: repaired via LLM retry"],
            }
        except Exception:
            pass
    new_retry = retry + (0 if ok else 1)
    return {"validation_ok": bool(ok), "retry_count": new_retry, "steps_log": logs}


def route_after_validate(state: InvoicePipelineState) -> Literal["extract", "end"]:
    if state.get("error"):
        return "end"
    if state.get("validation_ok"):
        return "end"
    # At most one re-extract after weak validation
    if int(state.get("retry_count") or 0) <= 1:
        return "extract"
    return "end"


def build_invoice_ingest_graph():
    """Linear workflow: ingest → OCR → extract → validate (optional re-extract)."""
    g = StateGraph(InvoicePipelineState)
    g.add_node("ingest", node_ingest)
    g.add_node("ocr", node_ocr)
    g.add_node("extract", node_extract)
    g.add_node("validate", node_validate)
    g.set_entry_point("ingest")
    g.add_edge("ingest", "ocr")
    g.add_edge("ocr", "extract")
    g.add_edge("extract", "validate")
    g.add_conditional_edges(
        "validate",
        route_after_validate,
        {"extract": "extract", "end": END},
    )
    return g.compile()


_invoice_ingest_app = None


def get_invoice_ingest_graph():
    global _invoice_ingest_app
    if _invoice_ingest_app is None:
        _invoice_ingest_app = build_invoice_ingest_graph()
    return _invoice_ingest_app


def run_invoice_ingest_workflow(file_path: str) -> dict[str, Any]:
    """Run full ingest pipeline; returns final state including steps_log."""
    app = get_invoice_ingest_graph()
    return app.invoke(
        {"file_path": file_path, "steps_log": [], "retry_count": 0}
    )
