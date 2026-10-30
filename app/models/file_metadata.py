"""File metadata ORM model."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.vault import Vault


class FileMetadata(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Stores metadata for encrypted files."""

    __tablename__ = "file_metadata"

    vault_id: Mapped[str] = mapped_column(String(36), ForeignKey("vaults.id"), nullable=False)
    original_name_enc: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_path: Mapped[str] = mapped_column(Text, nullable=False)
    nonce: Mapped[str] = mapped_column(String(64), nullable=False)
    hmac_tag: Mapped[str] = mapped_column(String(64), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    checksum: Mapped[str] = mapped_column(String(128), nullable=False)
    deleted_at: Mapped[str | None] = mapped_column(nullable=True)

    vault: Mapped[Vault] = relationship(back_populates="files")
