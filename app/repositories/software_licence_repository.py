"""Software licence repository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.software_licence import SoftwareLicence
from app.repositories.base_repository import BaseRepository


class SoftwareLicenceRepository(BaseRepository[SoftwareLicence]):
    """Repository for software licence data access."""

    def __init__(self, session: Session) -> None:
        super().__init__(SoftwareLicence, session)

    def get_by_vault(self, vault_id: str) -> list[SoftwareLicence]:
        """Get all software licences for a vault."""
        stmt = (
            select(SoftwareLicence)
            .where(SoftwareLicence.vault_id == vault_id)
            .order_by(SoftwareLicence.created_at.desc())
        )
        return list(self.session.execute(stmt).scalars().all())
