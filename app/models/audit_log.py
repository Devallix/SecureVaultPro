"""Audit log ORM model."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.vault import Vault


class AuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Tracks security-relevant events for audit purposes."""

    __tablename__ = "audit_logs"

    vault_id: Mapped[str] = mapped_column(String(36), ForeignKey("vaults.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    details_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    vault: Mapped[Vault] = relationship(back_populates="audit_logs")
