"""Shared pytest fixtures.

Tests run against a temporary file-based SQLite database (not ``:memory:``,
which would give each pooled connection its own separate database since our
routes run sync in FastAPI's threadpool). The env var must be set before any
``app`` import so the engine binds to it.
"""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient

_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_db_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"

from app.db.session import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    """A TestClient with a freshly created, empty schema per test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def register(client: TestClient, username: str = "alice", password: str = "secret1"):
    return client.post(
        "/api/auth/register", json={"username": username, "password": password}
    )
