"""Audit log repository with specialised queries."""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.base_repository import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    """Repository for audit log data access."""

    def __init__(self, session: Session) -> None:
        super().__init__(AuditLog, session)

    def get_by_vault(
        self,
        vault_id: str,
        limit: int = 100,
        offset: int = 0,
        action: str | None = None,
    ) -> list[AuditLog]:
        """Get audit logs for a vault with optional action filter."""
        stmt = select(AuditLog).where(AuditLog.vault_id == vault_id)
        if action:
            stmt = stmt.where(AuditLog.action == action)
        stmt = stmt.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def get_recent(self, vault_id: str, hours: int = 24) -> list[AuditLog]:
        """Get audit logs from the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        stmt = (
            select(AuditLog)
            .where(AuditLog.vault_id == vault_id, AuditLog.created_at >= cutoff)
            .order_by(AuditLog.created_at.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def log_event(
        self,
        vault_id: str,
        action: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        details_enc: str | None = None,
    ) -> AuditLog:
        """Create and persist a new audit log entry.

        Args:
            vault_id: The vault ID.
            action: The action performed.
            entity_type: Type of entity affected.
            entity_id: ID of entity affected.
            details_enc: Encrypted details.

        Returns:
            The created audit log entry.
        """
        entry = AuditLog(
            vault_id=vault_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details_enc=details_enc,
        )
        return self.create(entry)

    def cleanup_old_logs(self, vault_id: str, retention_days: int = 365) -> int:
        """Delete audit logs older than the retention period.

        Args:
            vault_id: The vault ID.
            retention_days: Number of days to retain.

        Returns:
            Number of deleted entries.
        """
        cutoff = datetime.now() - timedelta(days=retention_days)
        from sqlalchemy import delete

        stmt = delete(AuditLog).where(
            AuditLog.vault_id == vault_id,
            AuditLog.created_at < cutoff,
        )
        result = self.session.execute(stmt)
        return result.rowcount or 0
