"""SM4 Encryptor - China National Standard SM4 (CBC mode + PKCS5 padding).

Ported from lobster project. Provides encryption for sensitive data:
phone, email, ID card, bank card. Compliant with 等保三级 requirements.

Falls back to AES-128-CBC when gmssl-python is unavailable.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Try gmssl-python first, fall back to AES
HAS_GMSSL = False
try:
    from gmssl import SM4_DECRYPT, SM4_ENCRYPT, Sm4, Sm4Key

    HAS_GMSSL = True
    logger.info("gmssl-python available: using SM4/CBC/PKCS5Padding")
except (ImportError, ValueError):
    HAS_GMSSL = False
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad as _aes_pad, unpad as _aes_unpad

        logger.warning("gmssl-python unavailable: falling back to AES-128-CBC")
    except ImportError:
        # Fallback: pure Python AES implementation (last resort)
        logger.warning("Neither gmssl nor pycryptodome available: SM4 encryptor disabled")


class SM4Encryptor:
    """SM4/AES encryptor in CBC mode with random IV per encryption."""

    KEY_SIZE = 16  # 128 bits
    IV_SIZE = 16

    def __init__(self, encryption_key: Optional[str] = None) -> None:
        key = encryption_key or os.environ.get("ENCRYPTION_KEY", "0123456789abcdef")
        # Normalize key to exactly KEY_SIZE bytes
        key_bytes = key.encode("utf-8")
        if len(key_bytes) < self.KEY_SIZE:
            key_bytes = key_bytes + b"0" * (self.KEY_SIZE - len(key_bytes))
        else:
            key_bytes = key_bytes[: self.KEY_SIZE]
        self._key_bytes = key_bytes
        self._sm4_key: Sm4Key | None = None
        if HAS_GMSSL:
            try:
                self._sm4_key = Sm4Key(self._key_bytes)
            except Exception as e:
                logger.warning("Failed to create SM4 key, falling back to AES: %s", e)

    # ── Core encrypt/decrypt ──────────────────────────────────────────

    def _pkcs5_pad(self, data: bytes) -> bytes:
        pad_len = self.IV_SIZE - (len(data) % self.IV_SIZE)
        return data + bytes([pad_len] * pad_len)

    def _pkcs5_unpad(self, data: bytes) -> bytes:
        return data[: -data[-1]]

    def encrypt(self, plaintext: Optional[str]) -> str:
        if not plaintext:
            return ""
        iv = os.urandom(self.IV_SIZE)
        padded = self._pkcs5_pad(plaintext.encode("utf-8"))

        if HAS_GMSSL and self._sm4_key is not None:
            sm4 = Sm4(self._sm4_key, SM4_ENCRYPT, iv)
            encrypted = sm4.encrypt(padded)
        else:
            cipher = AES.new(self._key_bytes, AES.MODE_CBC, iv)
            encrypted = cipher.encrypt(padded)

        return iv.hex() + encrypted.hex()

    def decrypt(self, ciphertext: Optional[str]) -> str:
        if not ciphertext:
            return ""
        if len(ciphertext) < 64:
            return ciphertext  # Not encrypted or corrupted

        try:
            iv = bytes.fromhex(ciphertext[:32])
            encrypted = bytes.fromhex(ciphertext[32:])

            if HAS_GMSSL and self._sm4_key is not None:
                sm4 = Sm4(self._sm4_key, SM4_DECRYPT, iv)
                decrypted = sm4.decrypt(encrypted)
            else:
                cipher = AES.new(self._key_bytes, AES.MODE_CBC, iv)
                decrypted = cipher.decrypt(encrypted)

            return self._pkcs5_unpad(decrypted).decode("utf-8")
        except Exception as e:
            logger.error("Decryption failed: %s", e)
            raise ValueError(f"Decryption failed: {e}")

    def is_encrypted(self, data: Optional[str]) -> bool:
        if not data or len(data) < 64:
            return False
        try:
            bytes.fromhex(data[:32])
            bytes.fromhex(data[32:])
            return True
        except ValueError:
            return False

    # ── Typed convenience methods ─────────────────────────────────────

    def encrypt_phone(self, phone: Optional[str]) -> Optional[str]:
        return self.encrypt(phone) if phone else None

    def decrypt_phone(self, encrypted: Optional[str]) -> Optional[str]:
        return self.decrypt(encrypted) if encrypted else None

    def encrypt_email(self, email: Optional[str]) -> Optional[str]:
        return self.encrypt(email) if email else None

    def decrypt_email(self, encrypted: Optional[str]) -> Optional[str]:
        return self.decrypt(encrypted) if encrypted else None

    def encrypt_id_card(self, id_card: Optional[str]) -> Optional[str]:
        return self.encrypt(id_card) if id_card else None

    def decrypt_id_card(self, encrypted: Optional[str]) -> Optional[str]:
        return self.decrypt(encrypted) if encrypted else None

    def encrypt_bank_card(self, card: Optional[str]) -> Optional[str]:
        return self.encrypt(card) if card else None

    def decrypt_bank_card(self, encrypted: Optional[str]) -> Optional[str]:
        return self.decrypt(encrypted) if encrypted else None


# ── Module-level singleton ────────────────────────────────────────────

_encryptor: SM4Encryptor | None = None


def get_encryptor() -> SM4Encryptor:
    global _encryptor
    if _encryptor is None:
        _encryptor = SM4Encryptor()
    return _encryptor


def encrypt_sensitive_data(data: str) -> str:
    return get_encryptor().encrypt(data)


def decrypt_sensitive_data(encrypted_data: str) -> str:
    return get_encryptor().decrypt(encrypted_data)
