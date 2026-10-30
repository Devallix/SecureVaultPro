"""Password ORM model."""
from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.password_history import PasswordHistory
    from app.models.tag import Tag
    from app.models.vault import Vault


class Password(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Represents an encrypted password entry."""

    __tablename__ = "passwords"

    vault_id: Mapped[str] = mapped_column(String(36), ForeignKey("vaults.id"), nullable=False)
    title_enc: Mapped[str] = mapped_column(Text, nullable=False)
    username_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    password_enc: Mapped[str] = mapped_column(Text, nullable=False)
    url_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("categories.id"), nullable=True)
    is_favourite: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)

    vault: Mapped[Vault] = relationship(back_populates="passwords")
    category: Mapped[Category | None] = relationship(back_populates="passwords")
    tags: Mapped[list[Tag]] = relationship(secondary="password_tags", back_populates="passwords")
    history: Mapped[list[PasswordHistory]] = relationship(
        back_populates="password_entry", cascade="all, delete-orphan"
    )
