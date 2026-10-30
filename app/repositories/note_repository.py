"""Note repository with specialised queries."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.secure_note import SecureNote
from app.repositories.base_repository import BaseRepository


class NoteRepository(BaseRepository[SecureNote]):
    """Repository for secure note data access."""

    def __init__(self, session: Session) -> None:
        super().__init__(SecureNote, session)

    def get_by_vault(self, vault_id: str, limit: int = 100, offset: int = 0) -> list[SecureNote]:
        """Get all notes for a vault."""
        stmt = (
            select(SecureNote)
            .where(SecureNote.vault_id == vault_id)
            .order_by(SecureNote.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.execute(stmt).scalars().all())

    def count_by_vault(self, vault_id: str) -> int:
        """Count notes in a vault."""
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(SecureNote)
            .where(SecureNote.vault_id == vault_id)
        )
        return self.session.execute(stmt).scalar() or 0
