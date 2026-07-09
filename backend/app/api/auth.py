"""Authentication endpoints: register, login, logout, and the current user."""

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.api.deps import current_user
from app.core.config import settings
from app.core.security import hash_password, new_session_token, verify_password
from app.db.session import get_db
from app.models import Session, User
from app.schemas import Credentials, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _start_session(db: DbSession, response: Response, user: User) -> None:
    """Create a session row and set the httpOnly cookie on ``response``."""
    token = new_session_token()
    db.add(Session(token=token, user_id=user.id))
    db.commit()
    response.set_cookie(
        key=settings.session_cookie,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # one week
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(
    creds: Credentials, response: Response, db: DbSession = Depends(get_db)
) -> User:
    username = creds.username.strip()
    exists = db.scalar(select(User).where(User.username == username))
    if exists is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")

    user = User(username=username, password_hash=hash_password(creds.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    _start_session(db, response, user)
    return user


@router.post("/login", response_model=UserOut)
def login(
    creds: Credentials, response: Response, db: DbSession = Depends(get_db)
) -> User:
    user = db.scalar(select(User).where(User.username == creds.username.strip()))
    if user is None or not verify_password(creds.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")

    _start_session(db, response, user)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    session_token: str | None = Cookie(default=None, alias=settings.session_cookie),
    db: DbSession = Depends(get_db),
) -> Response:
    # Delete the session the cookie points to (if any), then clear the cookie.
    if session_token:
        session = db.get(Session, session_token)
        if session is not None:
            db.delete(session)
            db.commit()
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(settings.session_cookie)
    return response


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)) -> User:
    return user
