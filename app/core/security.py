import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from app.core.config import settings

_password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Return an Argon2id password hash. Never log the input password."""
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    """Verify a password without exposing password/hash details."""
    if not password_hash:
        return False
    try:
        return _password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def create_access_token(user_id: int) -> tuple[str, int]:
    expires_in = settings.access_token_expire_minutes * 60
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
        "type": "access",
        "jti": secrets.token_urlsafe(16),
    }
    token = jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm="HS256",
    )
    return token, expires_in


def create_refresh_token() -> tuple[str, str, datetime]:
    """Return raw token, SHA-256 digest for storage, and expiration."""
    raw_token = secrets.token_urlsafe(64)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    return raw_token, token_hash, expires_at


def hash_refresh_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def decode_access_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key.get_secret_value(),
        algorithms=["HS256"],
        options={"require": ["exp", "iat", "sub", "type"]},
    )
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Invalid token type")
    return payload
