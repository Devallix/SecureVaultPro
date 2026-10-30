"""Recovery key ORM model."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.vault import Vault


class RecoveryKey(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Stores hashed recovery keys for vault recovery."""

    __tablename__ = "recovery_keys"

    vault_id: Mapped[str] = mapped_column(String(36), ForeignKey("vaults.id"), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    encrypted_vault_key: Mapped[str | None] = mapped_column(String, nullable=True)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)

    vault: Mapped[Vault] = relationship(back_populates="recovery_keys")
