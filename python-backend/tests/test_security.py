"""Tests for security.py: SM3 hashing, JWT token creation/decode."""

from app.core.security import (
    create_token,
    create_refresh_token,
    decode_token,
    get_user_id_from_token,
    hash_password,
    verify_password,
)


def test_hash_password_format():
    hashed = hash_password("TestPass123!")
    assert hashed.startswith("sm3$")
    parts = hashed.split("$")
    assert len(parts) == 3
    assert len(parts[1]) == 32  # 16 bytes hex = 32 chars


def test_verify_password_correct():
    plain = "MySecureP@ss"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed)


def test_verify_password_incorrect():
    hashed = hash_password("correct")
    assert not verify_password("wrong", hashed)


def test_verify_password_invalid_format():
    assert not verify_password("anything", "not-a-valid-hash")
    assert not verify_password("anything", "md5$salt$digest")


def test_hash_password_unique():
    h1 = hash_password("same")
    h2 = hash_password("same")
    assert h1 != h2  # Different salts


def test_create_token():
    token = create_token("user123", {"role": "admin"})
    assert token is not None
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user123"
    assert payload["role"] == "admin"


def test_create_refresh_token():
    token = create_refresh_token("user123")
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user123"
    assert payload["type"] == "refresh"


def test_decode_invalid_token():
    assert decode_token("invalid.token.here") is None


def test_get_user_id_from_token():
    token = create_token("user456")
    user_id = get_user_id_from_token(token)
    assert user_id == "user456"
