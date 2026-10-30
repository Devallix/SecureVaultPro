"""Tests for SearchService — global search across passwords, notes, files."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.authentication.master_password import create_master_password
from app.database.base import Base
from app.models import Vault
from app.repositories.file_repository import FileRepository
from app.repositories.note_repository import NoteRepository
from app.repositories.password_repository import PasswordRepository
from app.services.password_service import PasswordService
from app.services.search_service import SearchService


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
def search_deps(db_session, vault_with_key):
    vault, vault_key = vault_with_key
    pw_repo = PasswordRepository(db_session)
    note_repo = NoteRepository(db_session)
    file_repo = FileRepository(db_session)
    pw_service = PasswordService(vault_key, pw_repo, db_session)
    search_service = SearchService(vault_key, pw_repo, note_repo, file_repo)
    return search_service, pw_service, vault


class TestSearchService:
    def test_search_passwords(self, search_deps, db_session):
        search, pw_service, vault = search_deps
        pw_service.create_password(vault.id, "GitHub Login", "user@gh.com", "pass1")
        pw_service.create_password(vault.id, "Gmail Account", "user@gmail.com", "pass2")

        results = search.search(vault.id, "GitHub")
        assert len(results) == 1
        assert results[0]["type"] == "password"
        assert results[0]["title"] == "GitHub Login"

    def test_search_notes(self, search_deps, db_session):
        search, pw_service, vault = search_deps
        note_repo = NoteRepository(db_session)
        from app.services.note_service import NoteService

        note_service = NoteService(
            pw_service._key, note_repo
        )
        note_service.create_note(vault.id, "Meeting Notes", "Discuss Q4 roadmap")
        note_service.create_note(vault.id, "Shopping List", "Milk, eggs, bread")

        results = search.search(vault.id, "Meeting")
        assert len(results) == 1
        assert results[0]["type"] == "note"
        assert results[0]["title"] == "Meeting Notes"

    def test_search_no_results(self, search_deps):
        search, pw_service, vault = search_deps

        results = search.search(vault.id, "nonexistent")
        assert results == []

    def test_search_case_insensitive(self, search_deps):
        search, pw_service, vault = search_deps
        pw_service.create_password(vault.id, "Netflix Subscription", "user@netflix.com", "pass")

        results_upper = search.search(vault.id, "NETFLIX")
        results_lower = search.search(vault.id, "netflix")
        results_mixed = search.search(vault.id, "NeTfLiX")

        assert len(results_upper) == 1
        assert len(results_lower) == 1
        assert len(results_mixed) == 1
        assert results_upper[0]["title"] == "Netflix Subscription"
