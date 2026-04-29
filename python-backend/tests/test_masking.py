"""Tests for app/core/masking.py — pure data masking functions."""

from __future__ import annotations

import pytest

from app.core.masking import (
    mask_phone,
    mask_email,
    mask_id_card,
    mask_bank_card,
    mask_name,
    mask_address,
    mask_password,
    mask_token,
    mask_sensitive_data,
)


# ── mask_phone ────────────────────────────────────────────────────────

@pytest.mark.parametrize("input_val,expected", [
    (None, None),
    ("", ""),
    ("123", "123"),                    # too short (< 7)
    ("123456", "123456"),             # exactly 6, too short
    ("1381234", "138****1234"),          # minimum 7 chars: first 3 + **** + last 4
    ("13812345678", "138****5678"),    # standard Chinese phone
])
def test_mask_phone(input_val: str, expected: str):
    assert mask_phone(input_val) == expected


# ── mask_email ────────────────────────────────────────────────────────

@pytest.mark.parametrize("input_val,expected", [
    (None, None),
    ("", ""),
    ("noatsign", "noatsign"),          # no @ symbol
    ("a@example.com", "*@example.com"), # single char local
    ("ab@example.com", "ab***@example.com"), # two char local
    ("user@example.com", "us***@example.com"),
])
def test_mask_email(input_val: str, expected: str):
    assert mask_email(input_val) == expected


# ── mask_id_card ──────────────────────────────────────────────────────

@pytest.mark.parametrize("input_val,expected", [
    (None, None),
    ("", ""),
    ("123456", "123456"),              # too short (< 10)
    ("123456789", "123456789"),        # exactly 9, too short
    ("110101199001011234", "110101********1234"),  # standard 18-digit ID
])
def test_mask_id_card(input_val: str, expected: str):
    assert mask_id_card(input_val) == expected


# ── mask_bank_card ────────────────────────────────────────────────────

@pytest.mark.parametrize("input_val,expected", [
    (None, None),
    ("", ""),
    ("1234", "1234"),                  # too short (< 8)
    ("1234567", "1234567"),            # exactly 7, too short
    ("6222021234567890", "6222****7890"),  # standard bank card
])
def test_mask_bank_card(input_val: str, expected: str):
    assert mask_bank_card(input_val) == expected


# ── mask_name ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("input_val,expected", [
    (None, None),
    ("", ""),
    ("张", "张"),                       # single char
    ("张三", "张*"),                    # two chars
    ("张三丰", "张**"),                  # three chars
    ("欧阳明日", "欧***"),               # four chars
])
def test_mask_name(input_val: str, expected: str):
    assert mask_name(input_val) == expected


# ── mask_address ──────────────────────────────────────────────────────

@pytest.mark.parametrize("input_val,expected", [
    (None, None),
    ("", ""),
    ("Short", "Short"),                # < 10 chars
    ("123456789", "123456789"),        # exactly 9, too short
    ("1234567890", "1234567890***"),   # exactly 10
    ("12345678901234567890", "1234567890***"),  # 20 chars, first 10 + ###
])
def test_mask_address(input_val: str, expected: str):
    assert mask_address(input_val) == expected


# ── mask_password ─────────────────────────────────────────────────────

@pytest.mark.parametrize("input_val,expected", [
    (None, None),
    ("", ""),
    ("abc123", "****"),
    ("verylongpassword123", "****"),
])
def test_mask_password(input_val: str, expected: str):
    assert mask_password(input_val) == expected


# ── mask_token ────────────────────────────────────────────────────────

@pytest.mark.parametrize("input_val,expected", [
    (None, "***"),                      # None triggers "***"
    ("", "***"),                       # empty string triggers "***"
    ("short", "***"),                  # < 20 chars
    ("1234567890123456789", "***"),    # exactly 19, too short
    ("12345678901234567890", "12345678...34567890"),  # exactly 20: first 8 + ... + last 8
])
def test_mask_token(input_val: str, expected: str):
    assert mask_token(input_val) == expected


def test_mask_token_long():
    """Token > 20 chars: keep first 8 and last 8."""
    token = "abcdefghijklmnopqrs"  # 19 chars → "***"
    assert mask_token(token) == "***"

    token = "12345678901234567890"  # 20 chars
    result = mask_token(token)
    assert result == "12345678...34567890"

    token = "a" * 40
    result = mask_token(token)
    assert result == "aaaaaaaa...aaaaaaaa"
    assert "..." in result


# ── mask_sensitive_data (dispatcher) ─────────────────────────────────

def test_mask_sensitive_data_phone():
    assert mask_sensitive_data("13812345678", "phone") == "138****5678"


def test_mask_sensitive_data_email():
    assert mask_sensitive_data("user@example.com", "email") == "us***@example.com"


def test_mask_sensitive_data_id_card():
    assert mask_sensitive_data("110101199001011234", "id_card") == "110101********1234"


def test_mask_sensitive_data_bank_card():
    assert mask_sensitive_data("6222021234567890", "bank_card") == "6222****7890"


def test_mask_sensitive_data_name():
    assert mask_sensitive_data("张三丰", "name") == "张**"


def test_mask_sensitive_data_address():
    assert mask_sensitive_data("123456789012345 Main Street", "address") == "1234567890***"


def test_mask_sensitive_data_password():
    assert mask_sensitive_data("secret123", "password") == "****"


def test_mask_sensitive_data_token():
    result = mask_sensitive_data("12345678901234567890", "token")
    assert result == "12345678...34567890"


def test_mask_sensitive_data_unknown_type():
    """Unknown data_type returns data unchanged."""
    assert mask_sensitive_data("hello", "unknown") == "hello"


def test_mask_sensitive_data_none_with_type():
    """None data returns None regardless of type."""
    assert mask_sensitive_data(None, "phone") is None
