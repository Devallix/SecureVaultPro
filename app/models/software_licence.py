"""Software licence ORM model."""
from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.vault import Vault


class SoftwareLicence(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Stores encrypted software licence keys."""

    __tablename__ = "software_licences"

    vault_id: Mapped[str] = mapped_column(String(36), ForeignKey("vaults.id"), nullable=False)
    name_enc: Mapped[str] = mapped_column(Text, nullable=False)
    licence_key_enc: Mapped[str] = mapped_column(Text, nullable=False)
    publisher_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)

    vault: Mapped[Vault] = relationship(back_populates="software_licences")
