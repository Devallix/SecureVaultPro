"""Secure Note ORM model."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.tag import Tag
    from app.models.vault import Vault


class SecureNote(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Represents an encrypted secure note."""

    __tablename__ = "secure_notes"

    vault_id: Mapped[str] = mapped_column(String(36), ForeignKey("vaults.id"), nullable=False)
    title_enc: Mapped[str] = mapped_column(Text, nullable=False)
    content_enc: Mapped[str] = mapped_column(Text, nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False, default="markdown")

    vault: Mapped[Vault] = relationship(back_populates="notes")
    tags: Mapped[list[Tag]] = relationship(secondary="note_tags", back_populates="notes")
