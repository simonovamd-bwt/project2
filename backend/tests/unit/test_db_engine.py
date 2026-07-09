"""Unit tests for the adaptive engine builder in ``app.db.session``.

These assert the pooling/connection choices per database URL without touching
the module-level ``engine`` (which is bound to the test DATABASE_URL).
"""

from sqlalchemy.pool import StaticPool

from app.db.session import _is_in_memory_sqlite, _make_engine


def test_in_memory_sqlite_uses_static_pool():
    engine = _make_engine("sqlite://")
    assert isinstance(engine.pool, StaticPool)
    assert engine.dialect.name == "sqlite"


def test_explicit_memory_url_uses_static_pool():
    engine = _make_engine("sqlite:///:memory:")
    assert isinstance(engine.pool, StaticPool)


def test_file_sqlite_does_not_use_static_pool():
    engine = _make_engine("sqlite:///./some_file.db")
    assert not isinstance(engine.pool, StaticPool)
    assert engine.dialect.name == "sqlite"


def test_in_memory_sqlite_shares_one_database_across_connections():
    # StaticPool means every checkout is the SAME underlying connection, so a
    # table created on one session is visible on the next. Without it, in-memory
    # SQLite would give each threadpool connection its own empty database.
    from sqlalchemy import text

    engine = _make_engine("sqlite://")
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE t (id INTEGER)"))
        conn.execute(text("INSERT INTO t VALUES (1)"))
        conn.commit()
    # A separate connect() must still see the table (same shared connection).
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id FROM t")).fetchall()
    assert rows == [(1,)]


def test_in_memory_detection_helper():
    assert _is_in_memory_sqlite("sqlite://") is True
    assert _is_in_memory_sqlite("sqlite:///:memory:") is True
    assert _is_in_memory_sqlite("sqlite:///./pre_legal.db") is False
    assert _is_in_memory_sqlite("postgresql://localhost/db") is False
