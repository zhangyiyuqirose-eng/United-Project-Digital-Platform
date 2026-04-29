"""Security utilities: SM3 password hashing + JWT token management.

Replicates PasswordUtil.java (SM3 + salt) and JwtUtil.java (HMAC-SHA256).
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from gmssl import sm3, func
from jose import JWTError, jwt

from app.config import settings

# ── SM3 password hashing (matches Java PasswordUtil) ─────────────────

_SALT_LENGTH = 16


def _sm3_hex(data: str) -> str:
    """Compute SM3 hash and return hex digest."""
    from gmssl.sm3 import sm3_hash
    msg_bytes = [b for b in data.encode("utf-8")]
    return sm3_hash(msg_bytes)


def hash_password(plain: str) -> str:
    """Hash password with SM3 + random salt. Format: sm3$salt$digest"""
    salt = secrets.token_hex(_SALT_LENGTH)
    digest = _sm3_hex(plain + salt)
    return f"sm3${salt}${digest}"


def verify_password(plain: str, hashed: str) -> bool:
    """Verify plain password against stored sm3$salt$digest hash."""
    if not hashed.startswith("sm3$"):
        return False
    parts = hashed.split("$")
    if len(parts) != 3:
        return False
    _, salt, expected = parts
    return _sm3_hex(plain + salt) == expected


# ── JWT token management (matches Java JwtUtil) ──────────────────────

def create_token(user_id: str, claims: dict | None = None) -> str:
    """Create a JWT access token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=settings.jwt_expiration_seconds),
        **(claims or {}),
    }
    return jwt.encode(payload, settings.jwt_secret.get_secret_value(), algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> str:
    """Create a JWT refresh token (longer lived)."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=7),
    }
    return jwt.encode(payload, settings.jwt_secret.get_secret_value(), algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict | None:
    """Decode and validate a JWT token. Returns None if invalid/expired."""
    try:
        return jwt.decode(token, settings.jwt_secret.get_secret_value(), algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> str | None:
    """Extract user_id (sub) from JWT token."""
    payload = decode_token(token)
    return payload.get("sub") if payload else None
