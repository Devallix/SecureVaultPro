"""Secure notes service for SecureVault Pro."""
from __future__ import annotations

from typing import TYPE_CHECKING

from app.logging.logger import get_logger
from app.security.crypto_engine import CryptoEngine

if TYPE_CHECKING:
    from app.models.secure_note import SecureNote

logger = get_logger(__name__)


class NoteService:
    """Service for managing secure notes."""

    def __init__(self, vault_key: bytes, note_repo) -> None:
        self._key = vault_key
        self._repo = note_repo
        self._crypto = CryptoEngine()

    def create_note(self, vault_id: str, title: str, content: str, fmt: str = "markdown") -> SecureNote:
        """Create a new secure note."""
        from app.models.secure_note import SecureNote

        note = SecureNote(
            vault_id=vault_id,
            title_enc=self._crypto.encrypt_field(self._key, title),
            content_enc=self._crypto.encrypt_field(self._key, content),
            format=fmt,
        )
        self._repo.create(note)
        logger.info("Secure note created: {title}", title=title[:20])
        return note

    def get_note(self, note_id: str) -> dict | None:
        """Get and decrypt a secure note."""
        note = self._repo.get_by_id(note_id)
        if note is None:
            return None
        return self._decrypt_note(note)

    def get_all_notes(self, vault_id: str) -> list[dict]:
        """Get all decrypted notes for a vault."""
        notes = self._repo.get_by_vault(vault_id)
        return [self._decrypt_note(n) for n in notes]

    def update_note(self, note_id: str, title: str | None = None, content: str | None = None) -> None:
        """Update a secure note."""
        note = self._repo.get_by_id(note_id)
        if note is None:
            return
        if title is not None:
            note.title_enc = self._crypto.encrypt_field(self._key, title)
        if content is not None:
            note.content_enc = self._crypto.encrypt_field(self._key, content)
        self._repo.update(note)

    def delete_note(self, note_id: str) -> bool:
        """Delete a secure note."""
        return self._repo.delete_by_id(note_id)

    def _decrypt_note(self, note) -> dict:
        return {
            "id": note.id,
            "title": self._crypto.decrypt_field(self._key, note.title_enc),
            "content": self._crypto.decrypt_field(self._key, note.content_enc),
            "format": note.format,
            "created_at": note.created_at,
            "updated_at": note.updated_at,
        }
