from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

# Passwords are hashed with bcrypt directly (no passlib: unmaintained).
# Hashes are standard "$2b$..." strings, so accounts created with the
# previous passlib-based code keep working.


def hash_password(password: str) -> str:
    """Takes a plain password and returns its bcrypt hash."""
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time check of a plain password against a stored hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(user_id: str) -> str:
    """Signed JWT carrying the user id ("sub"), valid ACCESS_TOKEN_EXPIRE_MINUTES."""
    payload = {
        "sub": user_id,
        "exp": _now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Returns the user id inside a valid token, None otherwise."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        return None
    if payload.get("purpose"):  # not an access token (e.g. Spotify OAuth state)
        return None
    return payload.get("sub")


def create_state_token(user_id: str, purpose: str, minutes: int = 10) -> str:
    """Short-lived signed token, used as the OAuth "state" parameter so a
    Spotify callback can't be forged to attach an account to someone else."""
    payload = {"sub": user_id, "purpose": purpose, "exp": _now() + timedelta(minutes=minutes)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_state_token(token: str, purpose: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        return None
    if payload.get("purpose") != purpose:
        return None
    return payload.get("sub")
