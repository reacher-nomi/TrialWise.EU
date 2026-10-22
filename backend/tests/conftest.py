"""Test setup: use a throwaway SQLite file instead of PostgreSQL.

This must run BEFORE the app is imported, so the engine picks up this URL.
That way tests run anywhere (CI, laptop) without starting a database.
"""

import os
import tempfile

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"
os.environ["APP_ENV"] = "test"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as c:  # "with" triggers startup -> tables are created
        yield c
