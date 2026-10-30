"""Category ORM model."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.password import Password
    from app.models.vault import Vault


class Category(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Represents a category for organizing entries."""

    __tablename__ = "categories"

    vault_id: Mapped[str] = mapped_column(String(36), ForeignKey("vaults.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)

    vault: Mapped[Vault] = relationship(back_populates="categories")
    passwords: Mapped[list[Password]] = relationship(back_populates="category")
