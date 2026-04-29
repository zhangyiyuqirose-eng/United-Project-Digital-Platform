"""Data masking utilities for sensitive information display.

Compliant with 等保三级 requirements. Used in logs, API responses, and UI.
"""

from __future__ import annotations

from typing import Optional


def mask_phone(phone: Optional[str]) -> Optional[str]:
    """Mask phone: keep first 3 and last 4 digits."""
    if not phone or len(phone) < 7:
        return phone
    return f"{phone[:3]}****{phone[-4:]}"


def mask_email(email: Optional[str]) -> Optional[str]:
    """Mask email: keep first 2 chars and domain."""
    if not email or "@" not in email:
        return email
    local, domain = email.split("@", 1)
    if len(local) < 2:
        return f"*@{domain}"
    return f"{local[:2]}***@{domain}"


def mask_id_card(id_card: Optional[str]) -> Optional[str]:
    """Mask ID card: keep first 6 and last 4 digits."""
    if not id_card or len(id_card) < 10:
        return id_card
    return f"{id_card[:6]}********{id_card[-4:]}"


def mask_bank_card(card: Optional[str]) -> Optional[str]:
    """Mask bank card: keep first 4 and last 4 digits."""
    if not card or len(card) < 8:
        return card
    return f"{card[:4]}****{card[-4:]}"


def mask_name(name: Optional[str]) -> Optional[str]:
    """Mask name: keep first character."""
    if not name or len(name) < 2:
        return name
    return f"{name[0]}{'*' * (len(name) - 1)}"


def mask_address(address: Optional[str]) -> Optional[str]:
    """Mask address: keep first 10 chars."""
    if not address or len(address) < 10:
        return address
    return f"{address[:10]}***"


def mask_password(_password: Optional[str]) -> Optional[str]:
    """Mask password: always show ****."""
    if not _password:
        return _password
    return "****"


def mask_token(token: Optional[str]) -> Optional[str]:
    """Mask token: keep first 8 and last 8 chars."""
    if not token or len(token) < 20:
        return "***"
    return f"{token[:8]}...{token[-8:]}"


def mask_sensitive_data(data: Optional[str], data_type: str) -> Optional[str]:
    """Generic masking dispatcher."""
    dispatch: dict[str, callable] = {
        "phone": mask_phone,
        "email": mask_email,
        "id_card": mask_id_card,
        "bank_card": mask_bank_card,
        "name": mask_name,
        "address": mask_address,
        "password": mask_password,
        "token": mask_token,
    }
    fn = dispatch.get(data_type)
    return fn(data) if fn else data
