"""Vault lock management with auto-lock support."""

from app.core.session import SessionManager
from app.logging.logger import get_logger

logger = get_logger(__name__)


def lock_vault_and_session(session: SessionManager) -> None:
    """Lock the vault and end the session.

    Args:
        session: The session manager instance.
    """
    session.lock()
    logger.info("Vault and session locked")
