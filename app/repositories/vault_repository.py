"""Repository for Vault ORM operations."""

from datetime import UTC

from sqlalchemy.orm import Session

from app.models.vault import Vault
from app.repositories.base_repository import BaseRepository


class VaultRepository(BaseRepository[Vault]):
    """Repository for vault-specific database operations."""

    def __init__(self, session: Session) -> None:
        super().__init__(Vault, session)

    def get_first(self) -> Vault | None:
        return self.session.query(Vault).first()

    def get_by_name(self, name: str) -> Vault | None:
        return self.session.query(Vault).filter(Vault.name == name).first()

    def mark_unlocked(self, vault_id: str) -> None:
        vault = self.get_by_id(vault_id)
        if vault:
            from datetime import datetime

            vault.is_locked = False
            vault.last_unlocked_at = datetime.now(UTC)
            self.session.flush()

    def mark_locked(self, vault_id: str) -> None:
        vault = self.get_by_id(vault_id)
        if vault:
            vault.is_locked = True
            self.session.flush()
