"""SSH Key ORM model."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.vault import Vault


class SSHKey(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Stores encrypted SSH key pairs."""

    __tablename__ = "ssh_keys"

    vault_id: Mapped[str] = mapped_column(String(36), ForeignKey("vaults.id"), nullable=False)
    name_enc: Mapped[str] = mapped_column(Text, nullable=False)
    public_key_enc: Mapped[str] = mapped_column(Text, nullable=False)
    private_key_enc: Mapped[str] = mapped_column(Text, nullable=False)
    key_type: Mapped[str] = mapped_column(String(20), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    last_used_at: Mapped[str | None] = mapped_column(nullable=True)

    vault: Mapped[Vault] = relationship(back_populates="ssh_keys")
