"""API key repository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.api_key import APIKey
from app.repositories.base_repository import BaseRepository


class APIKeyRepository(BaseRepository[APIKey]):
    """Repository for API key data access."""

    def __init__(self, session: Session) -> None:
        super().__init__(APIKey, session)

    def get_by_vault(self, vault_id: str) -> list[APIKey]:
        """Get all API keys for a vault."""
        stmt = (
            select(APIKey)
            .where(APIKey.vault_id == vault_id)
            .order_by(APIKey.created_at.desc())
        )
        return list(self.session.execute(stmt).scalars().all())
