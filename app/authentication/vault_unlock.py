"""Vault unlock/lock logic for SecureVault Pro."""

from datetime import datetime

from app.logging.logger import get_logger

logger = get_logger(__name__)


def unlock_vault(vault_key: bytes, vault) -> None:
    """Unlock a vault and update its state.

    Args:
        vault: The Vault ORM model instance.
        vault_key: The derived vault key.
    """
    vault.is_locked = False
    vault.last_unlocked_at = datetime.now()
    logger.info("Vault '{name}' unlocked", name=vault.name)


def lock_vault(vault) -> None:
    """Lock a vault and update its state.

    Args:
        vault: The Vault ORM model instance.
    """
    vault.is_locked = True
    logger.info("Vault '{name}' locked", name=vault.name)
