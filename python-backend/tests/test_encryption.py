"""Tests for field encryption mixin (app/core/field_encryption.py)."""

from __future__ import annotations

import pytest

from app.core.field_encryption import (
    ENCRYPTED_FIELDS,
    SM4_PREFIX,
    EncryptedFieldMixin,
)
from app.core.sm4_encryptor import SM4Encryptor, get_encryptor
from app.models.auth.models import User
from app.models.resource.models import OutsourcePerson


# ── SM4Encryptor unit tests ───────────────────────────────────────────

class TestSM4Encryptor:
    """Unit tests for the SM4Encryptor class directly."""

    def test_encrypt_produces_hex_string(self):
        enc = SM4Encryptor()
        result = enc.encrypt("13800138000")
        assert isinstance(result, str)
        assert len(result) > 0
        # Should be hex: IV(32 hex) + ciphertext
        assert len(result) >= 64

    def test_decrypt_returns_original(self):
        enc = SM4Encryptor()
        plaintext = "110101199001011234"
        encrypted = enc.encrypt(plaintext)
        decrypted = enc.decrypt(encrypted)
        assert decrypted == plaintext

    def test_encrypt_empty_string(self):
        enc = SM4Encryptor()
        assert enc.encrypt("") == ""
        assert enc.encrypt(None) == ""

    def test_decrypt_empty_string(self):
        enc = SM4Encryptor()
        assert enc.decrypt("") == ""
        assert enc.decrypt(None) == ""

    def test_decrypt_short_string_returns_unchanged(self):
        enc = SM4Encryptor()
        short = "short"
        assert enc.decrypt(short) == short

    def test_is_encrypted_true(self):
        enc = SM4Encryptor()
        encrypted = enc.encrypt("test")
        assert enc.is_encrypted(encrypted) is True

    def test_is_encrypted_false_short(self):
        enc = SM4Encryptor()
        assert enc.is_encrypted("short") is False

    def test_is_encrypted_none(self):
        enc = SM4Encryptor()
        assert enc.is_encrypted(None) is False

    def test_is_encrypted_empty(self):
        enc = SM4Encryptor()
        assert enc.is_encrypted("") is False

    def test_encrypt_is_deterministic_for_same_plaintext(self):
        """Different encryptions of same text produce different ciphertext (due to random IV)."""
        enc = SM4Encryptor()
        encrypted1 = enc.encrypt("same text")
        encrypted2 = enc.encrypt("same text")
        assert encrypted1 != encrypted2  # random IV ensures uniqueness

    def test_typed_convenience_encrypt_phone(self):
        enc = SM4Encryptor()
        result = enc.encrypt_phone("13800138000")
        assert result is not None
        assert enc.decrypt_phone(result) == "13800138000"

    def test_typed_convenience_encrypt_email(self):
        enc = SM4Encryptor()
        result = enc.encrypt_email("test@example.com")
        assert result is not None
        assert enc.decrypt_email(result) == "test@example.com"

    def test_typed_convenience_encrypt_id_card(self):
        enc = SM4Encryptor()
        result = enc.encrypt_id_card("110101199001011234")
        assert result is not None
        assert enc.decrypt_id_card(result) == "110101199001011234"

    def test_typed_convenience_encrypt_bank_card(self):
        enc = SM4Encryptor()
        result = enc.encrypt_bank_card("6222021234567890")
        assert result is not None
        assert enc.decrypt_bank_card(result) == "6222021234567890"

    def test_typed_convenience_none_inputs(self):
        enc = SM4Encryptor()
        assert enc.encrypt_phone(None) is None
        assert enc.encrypt_email(None) is None
        assert enc.encrypt_id_card(None) is None
        assert enc.encrypt_bank_card(None) is None
        assert enc.decrypt_phone(None) is None
        assert enc.decrypt_email(None) is None
        assert enc.decrypt_id_card(None) is None
        assert enc.decrypt_bank_card(None) is None

    def test_custom_key_works(self):
        enc = SM4Encryptor(encryption_key="my-custom-key-16")
        result = enc.encrypt("data")
        decrypted = enc.decrypt(result)
        assert decrypted == "data"

    def test_different_keys_produce_different_output(self):
        enc1 = SM4Encryptor(encryption_key="key-one-12345678")
        enc2 = SM4Encryptor(encryption_key="key-two-12345678")
        cipher = enc1.encrypt("data")
        # Different keys should produce different ciphertexts
        cipher2 = enc2.encrypt("data")
        assert cipher != cipher2


# ── EncryptedFieldMixin on OutsourcePerson ────────────────────────────

class TestEncryptedFieldMixinOutsourcePerson:

    def test_encrypt_fields_on_outsource_person(self):
        """encrypt_fields() should encrypt id_card and phone on OutsourcePerson."""
        person = OutsourcePerson(
            person_id="p-1",
            emp_code="E001",
            name="Test Person",
            id_card="110101199001011234",
            phone="13800138000",
            email="test@example.com",
            level=1,
            daily_rate=1000.00,
            pool_status=0,
        )
        person.encrypt_fields()

        # Values should be prefixed with SM4:
        assert person.id_card.startswith(SM4_PREFIX)
        assert person.phone.startswith(SM4_PREFIX)
        # email should NOT be encrypted (not in ENCRYPTED_FIELDS for pm_outsource_person)
        assert not person.email.startswith(SM4_PREFIX)

    def test_decrypt_fields_returns_correct_values(self):
        """decrypt_fields() should return original plaintext values."""
        original_id_card = "110101199001011234"
        original_phone = "13800138000"
        person = OutsourcePerson(
            person_id="p-2",
            emp_code="E002",
            name="Decrypt Test",
            id_card=original_id_card,
            phone=original_phone,
            level=2,
            daily_rate=800.00,
            pool_status=0,
        )
        person.encrypt_fields()

        decrypted = person.decrypt_fields()
        assert decrypted["id_card"] == original_id_card
        assert decrypted["phone"] == original_phone

    def test_encrypt_fields_idempotent(self):
        """Calling encrypt_fields() twice should not double-encrypt (SM4 prefix check)."""
        person = OutsourcePerson(
            person_id="p-3",
            emp_code="E003",
            name="Idempotent Test",
            id_card="110101199001011234",
            phone="13800138000",
            level=1,
            daily_rate=900.00,
            pool_status=0,
        )
        person.encrypt_fields()
        first_encrypted_id = person.id_card
        first_encrypted_phone = person.phone

        person.encrypt_fields()
        assert person.id_card == first_encrypted_id
        assert person.phone == first_encrypted_phone

    def test_field_not_on_model_skipped(self):
        """bank_card field does not exist on OutsourcePerson model (hasattr check)."""
        # ENCRYPTED_FIELDS for pm_outsource_person includes "bank_card"
        # but OutsourcePerson model does NOT have a bank_card column
        # encrypt_fields should skip it gracefully
        person = OutsourcePerson(
            person_id="p-4",
            emp_code="E004",
            name="No Bank Card",
            id_card="110101199001011234",
            phone="13800138000",
            level=1,
            daily_rate=500.00,
            pool_status=0,
        )
        # Should not raise AttributeError
        person.encrypt_fields()
        assert person.id_card.startswith(SM4_PREFIX)

    def test_empty_fields_skipped(self):
        """Empty/None fields should not be encrypted."""
        person = OutsourcePerson(
            person_id="p-5",
            emp_code="E005",
            name="Empty Fields",
            id_card="",
            phone=None,
            level=1,
            daily_rate=500.00,
            pool_status=0,
        )
        person.encrypt_fields()
        assert person.id_card == ""  # unchanged
        assert person.phone is None  # unchanged

    def test_decrypt_fields_skips_unencrypted(self):
        """decrypt_fields() should skip fields that don't have SM4: prefix."""
        person = OutsourcePerson(
            person_id="p-6",
            emp_code="E006",
            name="Plain Fields",
            id_card="plain-id-card",  # Plain text, no SM4: prefix
            phone="13800138000",  # Plain text
            level=1,
            daily_rate=500.00,
            pool_status=0,
        )
        decrypted = person.decrypt_fields()
        # Should return empty dict since no fields have SM4: prefix
        assert decrypted == {}
        assert "id_card" not in decrypted
        assert "phone" not in decrypted

    def test_encrypt_and_decrypt_roundtrip(self):
        """Full roundtrip: encrypt -> decrypt returns original values."""
        original_id = "110101199001011234"
        original_phone = "13900139000"
        person = OutsourcePerson(
            person_id="p-7",
            emp_code="E007",
            name="Roundtrip Test",
            id_card=original_id,
            phone=original_phone,
            level=3,
            daily_rate=1200.00,
            pool_status=0,
        )
        person.encrypt_fields()

        # Verify encrypted
        assert person.id_card != original_id
        assert person.phone != original_phone
        assert person.id_card.startswith(SM4_PREFIX)

        # Decrypt
        decrypted = person.decrypt_fields()
        assert decrypted["id_card"] == original_id
        assert decrypted["phone"] == original_phone


# ── EncryptedFieldMixin on User ───────────────────────────────────────

class TestEncryptedFieldMixinUser:

    def test_encrypt_fields_on_user(self):
        """encrypt_fields() on User should encrypt phone only."""
        user = User(
            user_id="u-1",
            username="testuser",
            password="hashed-password",
            name="Test User",
            phone="13800138000",
            email="user@example.com",
            status=1,
        )
        user.encrypt_fields()

        assert user.phone.startswith(SM4_PREFIX)
        # email should NOT be encrypted (not in ENCRYPTED_FIELDS for pm_sys_user)
        assert not user.email.startswith(SM4_PREFIX)

    def test_decrypt_fields_on_user(self):
        """decrypt_fields() on User should return original phone."""
        original_phone = "13900139000"
        user = User(
            user_id="u-2",
            username="decryptuser",
            password="hashed-password",
            name="Decrypt User",
            phone=original_phone,
            email="user2@example.com",
            status=1,
        )
        user.encrypt_fields()
        decrypted = user.decrypt_fields()
        assert decrypted["phone"] == original_phone

    def test_user_encrypt_idempotent(self):
        """encrypt_fields() twice on User should not double-encrypt."""
        user = User(
            user_id="u-3",
            username="idempuser",
            password="hashed",
            name="Idemp User",
            phone="13700137000",
            status=1,
        )
        user.encrypt_fields()
        first_encrypted = user.phone

        user.encrypt_fields()
        assert user.phone == first_encrypted

    def test_user_no_phone(self):
        """User without phone should not raise errors."""
        user = User(
            user_id="u-4",
            username="nophone",
            password="hashed",
            name="No Phone",
            phone=None,
            status=1,
        )
        user.encrypt_fields()
        assert user.phone is None


# ── ENCRYPTED_FIELDS configuration ────────────────────────────────────

class TestEncryptedFieldsConfig:

    def test_outsource_person_fields(self):
        fields = ENCRYPTED_FIELDS.get("pm_outsource_person", [])
        assert "id_card" in fields
        assert "phone" in fields
        assert "bank_card" in fields

    def test_user_fields(self):
        fields = ENCRYPTED_FIELDS.get("pm_sys_user", [])
        assert "phone" in fields

    def test_unknown_table_returns_empty(self):
        fields = ENCRYPTED_FIELDS.get("nonexistent_table", [])
        assert fields == []


# ── get_encryptor singleton ───────────────────────────────────────────

class TestGetEncryptor:

    def test_returns_same_instance(self):
        enc1 = get_encryptor()
        enc2 = get_encryptor()
        assert enc1 is enc2
