"""Tag repository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.repositories.base_repository import BaseRepository


class TagRepository(BaseRepository[Tag]):
    """Repository for tag data access."""

    def __init__(self, session: Session) -> None:
        super().__init__(Tag, session)

    def get_by_vault(self, vault_id: str) -> list[Tag]:
        """Get all tags for a vault."""
        stmt = (
            select(Tag)
            .where(Tag.vault_id == vault_id)
            .order_by(Tag.name.asc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_by_name(self, vault_id: str, name: str) -> Tag | None:
        """Get a tag by name within a vault."""
        stmt = select(Tag).where(
            Tag.vault_id == vault_id,
            Tag.name == name,
        )
        return self.session.execute(stmt).scalars().first()
