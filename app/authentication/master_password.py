"""Master password management for SecureVault Pro.

Handles creation, verification, and change of the master password.
Uses Argon2id for key derivation and SHA-256 for verification hashing.
"""

import hashlib
import hmac

from app.core.constants import ARGON2_SALT_LEN
from app.core.exceptions import InvalidMasterPasswordError
from app.logging.logger import get_logger
from app.security.kdf import derive_key_argon2id
from app.security.secure_random import generate_salt

logger = get_logger(__name__)


def create_master_password(password: str) -> tuple[bytes, str, str]:
    """Create a new master password and derive the vault key.

    Args:
        password: The master password string.

    Returns:
        Tuple of (vault_key, salt_hex, verify_hash_hex).
    """
    salt = generate_salt(ARGON2_SALT_LEN)
    vault_key = derive_key_argon2id(password.encode("utf-8"), salt)

    verify_input = hashlib.sha256(password.encode("utf-8")).digest()
    verify_hash = hashlib.sha256(vault_key + verify_input).hexdigest()

    logger.info("Master password created")
    return vault_key, salt.hex(), verify_hash


def verify_master_password(password: str, salt_hex: str, expected_verify_hash: str) -> bytes:
    """Verify a master password and return the derived vault key.

    Args:
        password: The password to verify.
        salt_hex: Hex-encoded salt.
        expected_verify_hash: Expected verification hash.

    Returns:
        The derived vault key if verification succeeds.

    Raises:
        InvalidMasterPasswordError: If the password is incorrect.
    """
    salt = bytes.fromhex(salt_hex)
    vault_key = derive_key_argon2id(password.encode("utf-8"), salt)

    verify_input = hashlib.sha256(password.encode("utf-8")).digest()
    computed_hash = hashlib.sha256(vault_key + verify_input).hexdigest()

    if not hmac.compare_digest(computed_hash, expected_verify_hash):
        logger.warning("Master password verification failed")
        raise InvalidMasterPasswordError("Incorrect master password")

    logger.info("Master password verified successfully")
    return vault_key


def change_master_password(
    old_password: str,
    new_password: str,
    old_salt_hex: str,
    old_verify_hash: str,
) -> tuple[bytes, str, str]:
    """Change the master password and re-derive the vault key.

    Args:
        old_password: The current master password.
        new_password: The new master password.
        old_salt_hex: Current salt (hex).
        old_verify_hash: Current verify hash.

    Returns:
        Tuple of (new_vault_key, new_salt_hex, new_verify_hash).

    Raises:
        InvalidMasterPasswordError: If the old password is incorrect.
    """
    verify_master_password(old_password, old_salt_hex, old_verify_hash)
    logger.info("Old master password verified, creating new one")
    return create_master_password(new_password)
