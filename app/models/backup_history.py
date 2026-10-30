"""Backup history ORM model."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.vault import Vault


class BackupHistory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Tracks backup file history and integrity."""

    __tablename__ = "backup_history"

    vault_id: Mapped[str] = mapped_column(String(36), ForeignKey("vaults.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    algorithm: Mapped[str] = mapped_column(String(50), nullable=False)
    checksum: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="completed")

    vault: Mapped[Vault] = relationship(back_populates="backup_history")
