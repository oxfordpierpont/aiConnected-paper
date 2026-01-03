"""Encryption service for API keys."""

import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import settings


class EncryptionService:
    """Service for encrypting/decrypting sensitive data."""

    def __init__(self):
        self._fernet = self._create_fernet()

    def _create_fernet(self) -> Fernet:
        """Create a Fernet instance from the secret key."""
        # Derive a key from the secret
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"content_strategist_salt",  # In production, use a proper salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
        return Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string."""
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a string."""
        return self._fernet.decrypt(ciphertext.encode()).decode()


# Singleton instance
encryption_service = EncryptionService()
