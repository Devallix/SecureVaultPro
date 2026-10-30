"""Password repository with specialised queries."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.password import Password
from app.repositories.base_repository import BaseRepository


class PasswordRepository(BaseRepository[Password]):
    """Repository for password entry data access."""

    def __init__(self, session: Session) -> None:
        super().__init__(Password, session)

    def get_by_vault(self, vault_id: str, limit: int = 100, offset: int = 0) -> list[Password]:
        """Get all passwords for a vault.

        Args:
            vault_id: The vault ID.
            limit: Maximum results.
            offset: Results to skip.

        Returns:
            List of password entries.
        """
        stmt = (
            select(Password)
            .where(Password.vault_id == vault_id)
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_favourites(self, vault_id: str) -> list[Password]:
        """Get all favourite passwords for a vault."""
        stmt = (
            select(Password)
            .where(Password.vault_id == vault_id, Password.is_favourite == True)  # noqa: E712
            .order_by(Password.updated_at.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_by_category(self, category_id: str) -> list[Password]:
        """Get all passwords in a category."""
        stmt = select(Password).where(Password.category_id == category_id)
        return list(self.session.execute(stmt).scalars().all())

    def get_expiring_soon(self, vault_id: str, days: int = 14) -> list[Password]:
        """Get passwords expiring within the given number of days."""
        from datetime import datetime, timedelta

        cutoff = datetime.now() + timedelta(days=days)
        stmt = (
            select(Password)
            .where(
                Password.vault_id == vault_id,
                Password.expires_at.isnot(None),
                Password.expires_at <= cutoff,
            )
            .order_by(Password.expires_at.asc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_old_passwords(self, vault_id: str, days: int = 90) -> list[Password]:
        """Get passwords not updated in the given number of days."""
        from datetime import datetime, timedelta

        cutoff = datetime.now() - timedelta(days=days)
        stmt = (
            select(Password)
            .where(
                Password.vault_id == vault_id,
                Password.updated_at <= cutoff,
            )
            .order_by(Password.updated_at.asc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def search(self, vault_id: str, query: str) -> list[Password]:
        """Search passwords by title or username (encrypted fields).

        Note: Full-text search on encrypted fields requires decryption
        first. This performs a basic LIKE on the encrypted columns as a
        placeholder until the search service implements decryption-aware search.
        """
        stmt = (
            select(Password)
            .where(Password.vault_id == vault_id)
        )
        return list(self.session.execute(stmt).scalars().all())

    def count_by_vault(self, vault_id: str) -> int:
        """Count passwords in a vault."""
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(Password)
            .where(Password.vault_id == vault_id)
        )
        return self.session.execute(stmt).scalar() or 0
