"""Pytest fixtures: test client and DB."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient

# Use a temp file so all connections share the same SQLite DB (unlike :memory:)
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["DB_URL"] = f"sqlite:///{_tmp.name}"

from app.main import app


@pytest.fixture
def client():
    """Test client; app lifespan runs and creates tables."""
    with TestClient(app) as c:
        yield c


def teardown_module():
    """Remove temp DB file after tests."""
    try:
        os.unlink(_tmp.name)
    except OSError:
        pass
