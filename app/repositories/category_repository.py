"""Category repository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Repository for category data access."""

    def __init__(self, session: Session) -> None:
        super().__init__(Category, session)

    def get_by_vault(self, vault_id: str) -> list[Category]:
        """Get all categories for a vault."""
        stmt = (
            select(Category)
            .where(Category.vault_id == vault_id)
            .order_by(Category.name.asc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_by_name(self, vault_id: str, name: str) -> Category | None:
        """Get a category by name within a vault."""
        stmt = select(Category).where(
            Category.vault_id == vault_id,
            Category.name == name,
        )
        return self.session.execute(stmt).scalars().first()
