"""Password change wizard logic for SecureVault Pro.

Handles the process of changing the master password, including
re-encryption of all vault data with the new key.
"""

from app.authentication.master_password import change_master_password
from app.logging.logger import get_logger

logger = get_logger(__name__)


def execute_password_change(
    old_password: str,
    new_password: str,
    old_salt_hex: str,
    old_verify_hash: str,
) -> tuple[bytes, str, str]:
    """Execute a master password change.

    Args:
        old_password: Current master password.
        new_password: New master password.
        old_salt_hex: Current salt.
        old_verify_hash: Current verification hash.

    Returns:
        Tuple of (new_vault_key, new_salt_hex, new_verify_hash).

    Raises:
        InvalidMasterPasswordError: If old password is wrong.
    """
    new_key, new_salt, new_hash = change_master_password(
        old_password, new_password, old_salt_hex, old_verify_hash
    )
    logger.info("Master password changed successfully")
    return new_key, new_salt, new_hash
