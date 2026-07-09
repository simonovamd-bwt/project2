from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


def _is_in_memory_sqlite(url: str) -> bool:
    """True for SQLite URLs that live purely in memory.

    ``sqlite://`` (no path) and ``sqlite:///:memory:`` both name the anonymous
    in-memory database. Anything with a file path is on disk.
    """
    return url in ("sqlite://", "sqlite:///:memory:") or ":memory:" in url


def _make_engine(url: str) -> Engine:
    """Create an engine, adapting connection args to the backing database.

    - In-memory SQLite: a single shared connection (``StaticPool``) so every
      session — including ones opened on FastAPI's threadpool — sees the same
      database. Without this each pooled connection would get its own empty DB.
    - File-based SQLite: only ``check_same_thread=False`` (multiple threads may
      touch the one file).
    - Anything else (e.g. Postgres): ``pool_pre_ping=True`` to drop dead
      connections before use.
    """
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        if _is_in_memory_sqlite(url):
            return create_engine(
                url,
                connect_args=connect_args,
                poolclass=StaticPool,
                future=True,
            )
        return create_engine(url, connect_args=connect_args, future=True)
    return create_engine(url, pool_pre_ping=True, future=True)


engine = _make_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
