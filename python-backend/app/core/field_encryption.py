"""Field encryption mixin for PII protection using SM4.

Provides EncryptedFieldMixin that SQLAlchemy models inherit to automatically
encrypt/decrypt designated PII fields.  Uses the module-level SM4Encryptor
singleton from app.core.sm4_encryptor.

Encrypted values are stored with an "SM4:" prefix so that encrypt_fields()
is idempotent -- it skips values that already carry the prefix.
"""

from __future__ import annotations

import logging

from app.core.sm4_encryptor import get_encryptor

logger = logging.getLogger(__name__)

#: Table name -> list of column names whose values must be encrypted at rest.
ENCRYPTED_FIELDS: dict[str, list[str]] = {
    "pm_outsource_person": ["id_card", "phone", "bank_card"],
    "pm_sys_user": ["phone"],
}

#: Prefix prepended to encrypted ciphertext so we can detect already-encrypted values.
SM4_PREFIX: str = "SM4:"


class EncryptedFieldMixin:
    """Mixin for SQLAlchemy models that carry PII columns.

    Usage::

        class OutsourcePerson(EncryptedFieldMixin, Base):
            __tablename__ = "pm_outsource_person"
            ...

        # --- before INSERT / UPDATE ---
        person.encrypt_fields()
        db.add(person)
        await db.flush()

        # --- after SELECT ---
        decrypted = person.decrypt_fields()  # {"phone": "138xxxx", ...}
        response_dict.update(decrypted)
    """

    def encrypt_fields(self) -> None:
        """Encrypt every mapped PII column whose value is not already prefixed.

        Idempotent -- columns whose string value already starts with ``SM4:``
        are left untouched, so calling this repeatedly on the same instance
        is harmless.
        """
        encryptor = get_encryptor()
        table_name = self.__tablename__  # type: ignore[attr-defined]
        fields = ENCRYPTED_FIELDS.get(table_name, [])
        for field_name in fields:
            if not hasattr(self, field_name):
                continue
            value = getattr(self, field_name, None)
            if value and isinstance(value, str) and not value.startswith(SM4_PREFIX):
                try:
                    encrypted = encryptor.encrypt(value)
                    setattr(self, field_name, SM4_PREFIX + encrypted)
                except Exception:
                    logger.exception("Failed to encrypt %s.%s", table_name, field_name)

    def decrypt_fields(self) -> dict[str, str]:
        """Decrypt every mapped PII column and return ``{field_name: plaintext}``.

        Columns whose value does *not* start with ``SM4:`` are silently
        skipped, so unencrypted legacy data flows through without errors.
        """
        encryptor = get_encryptor()
        table_name = self.__tablename__  # type: ignore[attr-defined]
        fields = ENCRYPTED_FIELDS.get(table_name, [])
        result: dict[str, str] = {}
        for field_name in fields:
            if not hasattr(self, field_name):
                continue
            value = getattr(self, field_name, None)
            if value and isinstance(value, str) and value.startswith(SM4_PREFIX):
                try:
                    result[field_name] = encryptor.decrypt(value[len(SM4_PREFIX):])
                except Exception:
                    logger.exception("Failed to decrypt %s.%s", table_name, field_name)
                    result[field_name] = value  # return raw value on failure
        return result
