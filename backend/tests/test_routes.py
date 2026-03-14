"""Tests for API routes."""

import io

import pytest
from fastapi.testclient import TestClient


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_api_health(client: TestClient):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_invoices_empty(client: TestClient):
    r = client.get("/api/invoices")
    assert r.status_code == 200
    assert r.json() == []


def test_upload_file(client: TestClient):
    r = client.post(
        "/api/upload-file",
        files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert r.status_code == 200
    data = r.json()
    assert "saved_as" in data
    assert "path" in data


def test_match_invoice_not_found(client: TestClient):
    r = client.post("/api/match", json={"invoice_id": 99999, "po_id": None, "receipt_id": None})
    assert r.status_code == 200
    data = r.json()
    assert data["matched"] is False
    assert "not found" in data["message"].lower()


def test_tax_assist_invoice_not_found(client: TestClient):
    r = client.post("/api/tax-assist", json={"invoice_id": 99999})
    assert r.status_code == 404
