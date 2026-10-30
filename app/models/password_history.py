"""Password history ORM model."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.password import Password


class PasswordHistory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Stores previous passwords for a password entry."""

    __tablename__ = "password_history"

    password_id: Mapped[str] = mapped_column(String(36), ForeignKey("passwords.id"), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)

    password_entry: Mapped[Password] = relationship(back_populates="history")
