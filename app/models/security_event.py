"""Security event ORM model."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.vault import Vault


class SecurityEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Tracks security events separate from audit logs for analysis."""

    __tablename__ = "security_events"

    vault_id: Mapped[str] = mapped_column(String(36), ForeignKey("vaults.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="info")
    message_enc: Mapped[str] = mapped_column(Text, nullable=False)
    resolved: Mapped[bool] = mapped_column(default=False)

    vault: Mapped[Vault] = relationship(back_populates="security_events")
