"""Password hashing and session-token helpers."""

import secrets

import bcrypt


def hash_password(password: str) -> str:
    """Return a bcrypt hash for ``password`` (utf-8, salted)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Check ``password`` against a stored bcrypt hash, never raising."""
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"), password_hash.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


def new_session_token() -> str:
    """A URL-safe, unguessable session token."""
    return secrets.token_urlsafe(32)
