"""Vault ORM model."""
from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.api_key import APIKey
    from app.models.audit_log import AuditLog
    from app.models.backup_history import BackupHistory
    from app.models.category import Category
    from app.models.file_metadata import FileMetadata
    from app.models.password import Password
    from app.models.recovery_key import RecoveryKey
    from app.models.secure_note import SecureNote
    from app.models.security_event import SecurityEvent
    from app.models.software_licence import SoftwareLicence
    from app.models.ssh_key import SSHKey
    from app.models.tag import Tag
    from app.models.user_settings import UserSetting


class Vault(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Represents an encrypted vault."""

    __tablename__ = "vaults"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    algorithm_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    salt: Mapped[str] = mapped_column(String(64), nullable=False)
    verify_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    is_locked: Mapped[bool] = mapped_column(default=True)
    last_unlocked_at: Mapped[datetime | None] = mapped_column(nullable=True)

    passwords: Mapped[list[Password]] = relationship(back_populates="vault", cascade="all, delete-orphan")
    notes: Mapped[list[SecureNote]] = relationship(back_populates="vault", cascade="all, delete-orphan")
    files: Mapped[list[FileMetadata]] = relationship(back_populates="vault", cascade="all, delete-orphan")
    ssh_keys: Mapped[list[SSHKey]] = relationship(back_populates="vault", cascade="all, delete-orphan")
    api_keys: Mapped[list[APIKey]] = relationship(back_populates="vault", cascade="all, delete-orphan")
    audit_logs: Mapped[list[AuditLog]] = relationship(back_populates="vault", cascade="all, delete-orphan")
    categories: Mapped[list[Category]] = relationship(back_populates="vault", cascade="all, delete-orphan")
    tags: Mapped[list[Tag]] = relationship(back_populates="vault", cascade="all, delete-orphan")
    recovery_keys: Mapped[list[RecoveryKey]] = relationship(back_populates="vault", cascade="all, delete-orphan")
    backup_history: Mapped[list[BackupHistory]] = relationship(back_populates="vault", cascade="all, delete-orphan")
    user_settings: Mapped[list[UserSetting]] = relationship(back_populates="vault", cascade="all, delete-orphan")
    software_licences: Mapped[list[SoftwareLicence]] = relationship(back_populates="vault", cascade="all, delete-orphan")
    security_events: Mapped[list[SecurityEvent]] = relationship(back_populates="vault", cascade="all, delete-orphan")
