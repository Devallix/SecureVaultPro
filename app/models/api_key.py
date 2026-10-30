"""API Key ORM model."""
from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.vault import Vault


class APIKey(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Stores encrypted API keys."""

    __tablename__ = "api_keys"

    vault_id: Mapped[str] = mapped_column(String(36), ForeignKey("vaults.id"), nullable=False)
    name_enc: Mapped[str] = mapped_column(Text, nullable=False)
    key_value_enc: Mapped[str] = mapped_column(Text, nullable=False)
    service_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)

    vault: Mapped[Vault] = relationship(back_populates="api_keys")
