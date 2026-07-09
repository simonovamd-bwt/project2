"""Shared pytest fixtures.

Tests run against an in-memory SQLite database, so they need no disk file,
no Docker, and no Postgres. ``_make_engine`` uses ``StaticPool`` for in-memory
URLs, which shares one connection across threads — required because our sync
routes run in FastAPI's threadpool and would otherwise each see a separate
empty database. The env var is set before any ``app`` import so the engine
binds to it.
"""

import os

os.environ["DATABASE_URL"] = "sqlite://"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

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
