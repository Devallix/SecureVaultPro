"""Recovery key generation and verification for SecureVault Pro."""

import hmac

from app.logging.logger import get_logger
from app.security.kdf import derive_key_argon2id
from app.security.secure_random import generate_recovery_words, generate_salt

logger = get_logger(__name__)


def generate_recovery_key() -> tuple[list[str], bytes, str]:
    """Generate a new recovery key.

    Returns:
        Tuple of (word_list, salt, key_hash_hex).
    """
    words = generate_recovery_words(12)
    passphrase = " ".join(words)
    salt = generate_salt()
    key_hash = derive_key_argon2id(passphrase.encode("utf-8"), salt, hash_len=32)

    logger.info("Recovery key generated (12 words)")
    return words, salt, key_hash.hex()


def verify_recovery_key(passphrase: str, salt_hex: str, expected_hash_hex: str) -> bool:
    """Verify a recovery key passphrase.

    Args:
        passphrase: The recovery passphrase.
        salt_hex: Hex-encoded salt.
        expected_hash_hex: Expected hash.

    Returns:
        True if the recovery key is valid.
    """
    salt = bytes.fromhex(salt_hex)
    key_hash = derive_key_argon2id(passphrase.encode("utf-8"), salt, hash_len=32)
    return hmac.compare_digest(key_hash.hex(), expected_hash_hex)
