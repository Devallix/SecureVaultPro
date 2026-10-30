"""Audit logging service for SecureVault Pro."""

from app.logging.logger import get_logger

logger = get_logger(__name__)


class AuditService:
    """Service for recording and querying audit log entries."""

    def __init__(self, audit_repo) -> None:
        self._repo = audit_repo

    def log(
        self,
        vault_id: str,
        action: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
    ) -> None:
        """Log a security-relevant event.

        Args:
            vault_id: The vault ID.
            action: The action performed.
            entity_type: Type of entity affected.
            entity_id: ID of entity affected.
        """
        self._repo.log_event(vault_id, action, entity_type, entity_id)
        logger.debug("Audit: {action} on {entity}", action=action, entity=entity_type or "system")

    def get_recent(self, vault_id: str, hours: int = 24) -> list[dict]:
        """Get recent audit entries."""
        entries = self._repo.get_recent(vault_id, hours)
        return [
            {
                "id": e.id,
                "action": e.action,
                "entity_type": e.entity_type,
                "entity_id": e.entity_id,
                "created_at": e.created_at,
            }
            for e in entries
        ]

    def get_all(self, vault_id: str, limit: int = 100) -> list[dict]:
        """Get all audit entries with pagination."""
        entries = self._repo.get_by_vault(vault_id, limit=limit)
        return [
            {
                "id": e.id,
                "action": e.action,
                "entity_type": e.entity_type,
                "entity_id": e.entity_id,
                "created_at": e.created_at,
            }
            for e in entries
        ]
