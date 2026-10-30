"""Versioned vault encryption engine.

Handles encrypting and decrypting vault data with algorithm versioning
to support future algorithm upgrades without breaking existing vaults.
"""

import base64

from app.core.constants import CRYPTO_VERSION_1_AES_GCM, CRYPTO_VERSION_2_CHACHA20
from app.core.exceptions import DecryptionError, UnsupportedAlgorithmError
from app.logging.logger import get_logger

logger = get_logger(__name__)


def encrypt_vault_data(
    key: bytes,
    plaintext: bytes,
    version: int = CRYPTO_VERSION_1_AES_GCM,
    aad: bytes | None = None,
) -> str:
    """Encrypt data for vault storage with versioned algorithm selection.

    Output format: base64(version_byte + nonce + ciphertext)

    Args:
        key: 32-byte encryption key.
        plaintext: Data to encrypt.
        version: Algorithm version to use.
        aad: Additional authenticated data.

    Returns:
        Base64-encoded encrypted payload.

    Raises:
        UnsupportedAlgorithmError: If the version is not supported.
    """
    from app.security.secure_random import generate_nonce
    from app.security.symmetric import encrypt_aes_gcm, encrypt_chacha20

    if version == CRYPTO_VERSION_1_AES_GCM:
        nonce = generate_nonce(12)
        ciphertext = encrypt_aes_gcm(key, plaintext, nonce, aad)
        payload = b"\x01" + nonce + ciphertext
    elif version == CRYPTO_VERSION_2_CHACHA20:
        nonce = generate_nonce(12)
        ciphertext = encrypt_chacha20(key, plaintext, nonce, aad)
        payload = b"\x02" + nonce + ciphertext
    else:
        raise UnsupportedAlgorithmError(f"Crypto version {version} is not supported")

    return base64.b64encode(payload).decode("ascii")


def decrypt_vault_data(
    key: bytes,
    encoded_payload: str,
    aad: bytes | None = None,
) -> bytes:
    """Decrypt vault data, auto-detecting algorithm from version byte.

    Args:
        key: 32-byte encryption key.
        encoded_payload: Base64-encoded encrypted payload.
        aad: Additional authenticated data.

    Returns:
        Decrypted plaintext bytes.

    Raises:
        DecryptionError: If decryption fails.
        UnsupportedAlgorithmError: If the algorithm version is not supported.
    """
    from app.security.symmetric import decrypt_aes_gcm, decrypt_chacha20

    try:
        payload = base64.b64decode(encoded_payload)
    except Exception as e:
        raise DecryptionError(f"Invalid payload encoding: {e}") from e

    if len(payload) < 2:
        raise DecryptionError("Payload too short")

    version = payload[0]
    data = payload[1:]

    if version == 1:
        if len(data) < 12:
            raise DecryptionError("Invalid AES-GCM payload length")
        nonce = data[:12]
        ciphertext = data[12:]
        return decrypt_aes_gcm(key, ciphertext, nonce, aad)
    elif version == 2:
        if len(data) < 12:
            raise DecryptionError("Invalid ChaCha20 payload length")
        nonce = data[:12]
        ciphertext = data[12:]
        return decrypt_chacha20(key, ciphertext, nonce, aad)
    else:
        raise UnsupportedAlgorithmError(f"Crypto version {version} is not supported")
