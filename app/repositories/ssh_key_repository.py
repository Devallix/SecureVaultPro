"""SSH key repository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ssh_key import SSHKey
from app.repositories.base_repository import BaseRepository


class SSHKeyRepository(BaseRepository[SSHKey]):
    """Repository for SSH key data access."""

    def __init__(self, session: Session) -> None:
        super().__init__(SSHKey, session)

    def get_by_vault(self, vault_id: str) -> list[SSHKey]:
        """Get all SSH keys for a vault."""
        stmt = (
            select(SSHKey)
            .where(SSHKey.vault_id == vault_id)
            .order_by(SSHKey.created_at.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_by_fingerprint(self, fingerprint: str) -> SSHKey | None:
        """Get an SSH key by its fingerprint."""
        stmt = select(SSHKey).where(SSHKey.fingerprint == fingerprint)
        return self.session.execute(stmt).scalars().first()
