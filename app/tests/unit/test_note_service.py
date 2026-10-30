"""Tests for NoteService — secure notes CRUD and encryption roundtrip."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.authentication.master_password import create_master_password
from app.database.base import Base
from app.models import Vault
from app.repositories.note_repository import NoteRepository
from app.services.note_service import NoteService


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = factory()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture()
def vault_with_key(db_session):
    vault_key, salt_hex, verify_hash = create_master_password("TestPassword123!")
    vault = Vault(
        name="Test Vault",
        salt=salt_hex,
        verify_hash=verify_hash,
        is_locked=False,
        algorithm_version=1,
    )
    db_session.add(vault)
    db_session.commit()
    return vault, vault_key


@pytest.fixture()
def note_service(db_session, vault_with_key):
    vault, vault_key = vault_with_key
    repo = NoteRepository(db_session)
    return NoteService(vault_key, repo), vault


class TestNoteService:
    def test_create_note(self, db_session, note_service):
        service, vault = note_service
        note = service.create_note(vault.id, "My Title", "Some content here")

        assert note.id is not None
        assert note.vault_id == vault.id
        assert note.title_enc != "My Title"
        assert note.content_enc != "Some content here"

    def test_get_note(self, db_session, note_service):
        service, vault = note_service
        note = service.create_note(vault.id, "Secret Note", "Confidential data")

        result = service.get_note(note.id)
        assert result is not None
        assert result["title"] == "Secret Note"
        assert result["content"] == "Confidential data"
        assert result["format"] == "markdown"

    def test_get_all_notes(self, db_session, note_service):
        service, vault = note_service
        service.create_note(vault.id, "Note 1", "Body 1")
        service.create_note(vault.id, "Note 2", "Body 2")
        service.create_note(vault.id, "Note 3", "Body 3")

        notes = service.get_all_notes(vault.id)
        assert len(notes) == 3
        titles = {n["title"] for n in notes}
        assert titles == {"Note 1", "Note 2", "Note 3"}

    def test_update_note(self, db_session, note_service):
        service, vault = note_service
        note = service.create_note(vault.id, "Old Title", "Old content")

        service.update_note(note.id, title="New Title", content="New content")

        result = service.get_note(note.id)
        assert result["title"] == "New Title"
        assert result["content"] == "New content"

    def test_delete_note(self, db_session, note_service):
        service, vault = note_service
        note = service.create_note(vault.id, "Delete Me", "Gone soon")

        deleted = service.delete_note(note.id)
        assert deleted is True
        assert service.get_note(note.id) is None

    def test_decrypt_note_roundtrip(self, db_session, note_service):
        service, vault = note_service
        long_content = "A" * 500 + "!!!special chars: @#$%^&*()"
        note = service.create_note(vault.id, "Roundtrip Title", long_content)

        result = service.get_note(note.id)
        assert result["title"] == "Roundtrip Title"
        assert result["content"] == long_content
