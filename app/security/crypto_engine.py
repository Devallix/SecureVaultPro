"""Unified crypto engine facade for SecureVault Pro.

Provides a single interface for all cryptographic operations,
delegating to the appropriate specialized modules.
"""

import hmac

from app.core.constants import CURRENT_CRYPTO_VERSION
from app.logging.logger import get_logger

logger = get_logger(__name__)


class CryptoEngine:
    """Unified cryptographic operations facade.

    Provides symmetric/asymmetric encryption, hashing, key derivation,
    and vault data protection through a single interface.
    """

    def encrypt_field(self, key: bytes, plaintext: str, version: int | None = None) -> str:
        """Encrypt a string field for database storage.

        Args:
            key: 32-byte encryption key.
            plaintext: String to encrypt.
            version: Algorithm version (default: current).

        Returns:
            Base64-encoded encrypted payload.
        """
        from app.security.vault_crypto import encrypt_vault_data

        if version is None:
            version = CURRENT_CRYPTO_VERSION
        return encrypt_vault_data(key, plaintext.encode("utf-8"), version)

    def decrypt_field(self, key: bytes, ciphertext: str) -> str:
        """Decrypt a database field back to string.

        Args:
            key: 32-byte encryption key.
            ciphertext: Base64-encoded encrypted payload.

        Returns:
            Decrypted string.
        """
        from app.security.vault_crypto import decrypt_vault_data

        plaintext = decrypt_vault_data(key, ciphertext)
        return plaintext.decode("utf-8")

    def encrypt_bytes(self, key: bytes, data: bytes, version: int | None = None) -> str:
        """Encrypt raw bytes for storage.

        Args:
            key: 32-byte encryption key.
            data: Bytes to encrypt.
            version: Algorithm version.

        Returns:
            Base64-encoded encrypted payload.
        """
        from app.security.vault_crypto import encrypt_vault_data

        if version is None:
            version = CURRENT_CRYPTO_VERSION
        return encrypt_vault_data(key, data, version)

    def decrypt_bytes(self, key: bytes, ciphertext: str) -> bytes:
        """Decrypt stored bytes.

        Args:
            key: 32-byte encryption key.
            ciphertext: Base64-encoded encrypted payload.

        Returns:
            Decrypted bytes.
        """
        from app.security.vault_crypto import decrypt_vault_data

        return decrypt_vault_data(key, ciphertext)

    def derive_vault_key(self, password: str, salt: bytes) -> bytes:
        """Derive a vault encryption key from a master password.

        Uses Argon2id as the primary KDF.

        Args:
            password: Master password string.
            salt: Cryptographic salt.

        Returns:
            32-byte derived key.
        """
        from app.security.kdf import derive_key_argon2id

        return derive_key_argon2id(password.encode("utf-8"), salt)

    def generate_salt(self, length: int = 16) -> bytes:
        """Generate a cryptographic salt.

        Args:
            length: Salt length in bytes.

        Returns:
            Random salt bytes.
        """
        from app.security.secure_random import generate_salt as _gen_salt

        return _gen_salt(length)

    def compute_hash(self, data: bytes) -> str:
        """Compute a SHA-256 hash for integrity checking.

        Args:
            data: Data to hash.

        Returns:
            Hex-encoded hash string.
        """
        from app.security.hashing import hash_sha256

        return hash_sha256(data).hex()

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against a stored hash.

        Args:
            password: Password to verify.
            password_hash: Stored hex-encoded hash.

        Returns:
            True if the password matches.
        """
        from app.security.hashing import hash_sha256

        computed = hash_sha256(password.encode("utf-8")).hex()
        return hmac.compare_digest(computed, password_hash)

    def hash_password_for_storage(self, password: str) -> str:
        """Hash a password for storage (used for verification, not key derivation).

        Args:
            password: Password to hash.

        Returns:
            Hex-encoded hash string.
        """
        from app.security.hashing import hash_sha256

        return hash_sha256(password.encode("utf-8")).hex()
