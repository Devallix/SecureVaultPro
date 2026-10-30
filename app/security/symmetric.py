"""Symmetric encryption: AES-256-GCM and ChaCha20-Poly1305."""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from app.core.exceptions import DecryptionError, EncryptionError
from app.logging.logger import get_logger

logger = get_logger(__name__)


def encrypt_aes_gcm(key: bytes, plaintext: bytes, nonce: bytes, aad: bytes | None = None) -> bytes:
    """Encrypt data using AES-256-GCM.

    Args:
        key: 256-bit encryption key.
        plaintext: Data to encrypt.
        nonce: 96-bit nonce.
        optional aad: Additional authenticated data.

    Returns:
        ciphertext with appended authentication tag.

    Raises:
        EncryptionError: If encryption fails.
    """
    if len(key) != 32:
        raise EncryptionError(f"AES-256-GCM requires a 32-byte key, got {len(key)}")
    if len(nonce) != 12:
        raise EncryptionError(f"AES-256-GCM requires a 12-byte nonce, got {len(nonce)}")
    try:
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, aad)
        logger.debug("AES-256-GCM encrypted {size} bytes", size=len(plaintext))
        return ciphertext
    except Exception as e:
        raise EncryptionError(f"AES-256-GCM encryption failed: {e}") from e


def decrypt_aes_gcm(key: bytes, ciphertext: bytes, nonce: bytes, aad: bytes | None = None) -> bytes:
    """Decrypt data using AES-256-GCM.

    Args:
        key: 256-bit encryption key.
        ciphertext: Data to decrypt (with appended auth tag).
        nonce: 96-bit nonce used during encryption.
        optional aad: Additional authenticated data.

    Returns:
        Decrypted plaintext bytes.

    Raises:
        DecryptionError: If decryption or authentication fails.
    """
    if len(key) != 32:
        raise DecryptionError(f"AES-256-GCM requires a 32-byte key, got {len(key)}")
    if len(nonce) != 12:
        raise DecryptionError(f"AES-256-GCM requires a 12-byte nonce, got {len(nonce)}")
    try:
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, aad)
        logger.debug("AES-256-GCM decrypted {size} bytes", size=len(plaintext))
        return plaintext
    except Exception as e:
        raise DecryptionError(f"AES-256-GCM decryption failed (data may be corrupted or tampered): {e}") from e


def encrypt_chacha20(key: bytes, plaintext: bytes, nonce: bytes, aad: bytes | None = None) -> bytes:
    """Encrypt data using ChaCha20-Poly1305.

    Args:
        key: 256-bit encryption key.
        plaintext: Data to encrypt.
        nonce: 96-bit nonce.
        optional aad: Additional authenticated data.

    Returns:
        ciphertext with appended authentication tag.

    Raises:
        EncryptionError: If encryption fails.
    """
    if len(key) != 32:
        raise EncryptionError(f"ChaCha20-Poly1305 requires a 32-byte key, got {len(key)}")
    if len(nonce) != 12:
        raise EncryptionError(f"ChaCha20-Poly1305 requires a 12-byte nonce, got {len(nonce)}")
    try:
        chacha = ChaCha20Poly1305(key)
        ciphertext = chacha.encrypt(nonce, plaintext, aad)
        logger.debug("ChaCha20-Poly1305 encrypted {size} bytes", size=len(plaintext))
        return ciphertext
    except Exception as e:
        raise EncryptionError(f"ChaCha20-Poly1305 encryption failed: {e}") from e


def decrypt_chacha20(key: bytes, ciphertext: bytes, nonce: bytes, aad: bytes | None = None) -> bytes:
    """Decrypt data using ChaCha20-Poly1305.

    Args:
        key: 256-bit encryption key.
        ciphertext: Data to decrypt.
        nonce: 96-bit nonce.
        optional aad: Additional authenticated data.

    Returns:
        Decrypted plaintext bytes.

    Raises:
        DecryptionError: If decryption fails.
    """
    if len(key) != 32:
        raise DecryptionError(f"ChaCha20-Poly1305 requires a 32-byte key, got {len(key)}")
    if len(nonce) != 12:
        raise DecryptionError(f"ChaCha20-Poly1305 requires a 12-byte nonce, got {len(nonce)}")
    try:
        chacha = ChaCha20Poly1305(key)
        plaintext = chacha.decrypt(nonce, ciphertext, aad)
        logger.debug("ChaCha20-Poly1305 decrypted {size} bytes", size=len(plaintext))
        return plaintext
    except Exception as e:
        raise DecryptionError(f"ChaCha20-Poly1305 decryption failed: {e}") from e
