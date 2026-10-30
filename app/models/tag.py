"""Tag ORM model with association tables."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.password import Password
    from app.models.secure_note import SecureNote
    from app.models.vault import Vault

password_tags = Table(
    "password_tags",
    Base.metadata,
    Column("password_id", String(36), ForeignKey("passwords.id"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("tags.id"), primary_key=True),
)

note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", String(36), ForeignKey("secure_notes.id"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Represents a tag for organizing entries."""

    __tablename__ = "tags"

    vault_id: Mapped[str] = mapped_column(String(36), ForeignKey("vaults.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    vault: Mapped[Vault] = relationship(back_populates="tags")
    passwords: Mapped[list[Password]] = relationship(secondary=password_tags, back_populates="tags")
    notes: Mapped[list[SecureNote]] = relationship(secondary=note_tags, back_populates="tags")
