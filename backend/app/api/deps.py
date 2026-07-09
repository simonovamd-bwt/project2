"""Shared FastAPI dependencies."""

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.core.config import settings
from app.db.session import get_db
from app.models import Session, User


def current_user(
    db: DbSession = Depends(get_db),
    session_token: str | None = Cookie(default=None, alias=settings.session_cookie),
) -> User:
    """Resolve the logged-in user from the session cookie, or 401."""
    if not session_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")

    session = db.get(Session, session_token)
    if session is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid session")
    return session.user
