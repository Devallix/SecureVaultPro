"""User settings ORM model."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.vault import Vault


class UserSetting(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Stores encrypted user settings per vault."""

    __tablename__ = "user_settings"

    vault_id: Mapped[str] = mapped_column(String(36), ForeignKey("vaults.id"), nullable=False)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value_enc: Mapped[str] = mapped_column(Text, nullable=False)

    vault: Mapped[Vault] = relationship(back_populates="user_settings")
