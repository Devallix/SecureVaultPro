"""Recovery key repository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.recovery_key import RecoveryKey
from app.repositories.base_repository import BaseRepository


class RecoveryKeyRepository(BaseRepository[RecoveryKey]):
    """Repository for recovery key access."""

    def __init__(self, session: Session) -> None:
        super().__init__(RecoveryKey, session)

    def get_by_vault(self, vault_id: str) -> list[RecoveryKey]:
        """Get all recovery keys for a vault."""
        stmt = (
            select(RecoveryKey)
            .where(RecoveryKey.vault_id == vault_id)
            .order_by(RecoveryKey.created_at.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_active_by_vault(self, vault_id: str) -> RecoveryKey | None:
        """Get the active (unused) recovery key for a vault."""
        stmt = (
            select(RecoveryKey)
            .where(
                RecoveryKey.vault_id == vault_id,
                RecoveryKey.is_used == False,  # noqa: E712
            )
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()
