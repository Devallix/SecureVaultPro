"""SQLAlchemy declarative base and shared column mixins."""
from __future__ import annotations

import uuid
from datetime import datetime  # noqa: TC003

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _generate_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


class TimestampMixin:
    """Mixin that adds created_at and updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    """Mixin that adds a UUID primary key column."""

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=_generate_uuid,
    )
