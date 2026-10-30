"""File metadata repository with specialised queries."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.file_metadata import FileMetadata
from app.repositories.base_repository import BaseRepository


class FileRepository(BaseRepository[FileMetadata]):
    """Repository for encrypted file metadata access."""

    def __init__(self, session: Session) -> None:
        super().__init__(FileMetadata, session)

    def get_by_vault(self, vault_id: str, limit: int = 100, offset: int = 0) -> list[FileMetadata]:
        """Get all file entries for a vault."""
        stmt = (
            select(FileMetadata)
            .where(FileMetadata.vault_id == vault_id, FileMetadata.deleted_at.is_(None))
            .order_by(FileMetadata.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_deleted(self, vault_id: str) -> list[FileMetadata]:
        """Get soft-deleted files for a vault."""
        stmt = (
            select(FileMetadata)
            .where(FileMetadata.vault_id == vault_id, FileMetadata.deleted_at.isnot(None))
        )
        return list(self.session.execute(stmt).scalars().all())

    def count_by_vault(self, vault_id: str) -> int:
        """Count active files in a vault."""
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(FileMetadata)
            .where(FileMetadata.vault_id == vault_id, FileMetadata.deleted_at.is_(None))
        )
        return self.session.execute(stmt).scalar() or 0

    def total_size_by_vault(self, vault_id: str) -> int:
        """Get total file size for a vault."""
        from sqlalchemy import func

        stmt = (
            select(func.coalesce(func.sum(FileMetadata.file_size), 0))
            .where(FileMetadata.vault_id == vault_id, FileMetadata.deleted_at.is_(None))
        )
        return self.session.execute(stmt).scalar() or 0
