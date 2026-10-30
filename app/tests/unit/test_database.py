"""Tests for database engine and repository CRUD operations."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.authentication.master_password import create_master_password
from app.database.base import Base
from app.models.password import Password
from app.models.secure_note import SecureNote
from app.models.vault import Vault
from app.repositories.base_repository import BaseRepository
from app.repositories.vault_repository import VaultRepository
from app.security.secure_random import generate_salt


@pytest.fixture()
def db_session():
    """Create an in-memory SQLite database and session for each test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    test_session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = test_session_factory()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture()
def vault_with_key(db_session):
    """Create a vault in the test database and return (vault, vault_key)."""
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


class TestBaseRepository:
    def test_create_and_get(self, db_session) -> None:
        vault = Vault(
            name="Repo Test",
            salt=generate_salt(16).hex(),
            verify_hash="abc123",
            algorithm_version=1,
        )
        repo = BaseRepository(Vault, db_session)
        created = repo.create(vault)
        db_session.commit()

        fetched = repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.name == "Repo Test"

    def test_get_all(self, db_session) -> None:
        salt_hex = generate_salt(16).hex()
        for i in range(3):
            db_session.add(Vault(
                name=f"Vault {i}",
                salt=salt_hex,
                verify_hash="h",
                algorithm_version=1,
            ))
        db_session.commit()

        repo = BaseRepository(Vault, db_session)
        all_vaults = repo.get_all()
        assert len(all_vaults) == 3

    def test_count(self, db_session) -> None:
        repo = BaseRepository(Vault, db_session)
        assert repo.count() == 0

        db_session.add(Vault(name="V", salt="s", verify_hash="h", algorithm_version=1))
        db_session.commit()
        assert repo.count() == 1

    def test_delete_by_id(self, db_session) -> None:
        vault = Vault(name="Del", salt="s", verify_hash="h", algorithm_version=1)
        db_session.add(vault)
        db_session.commit()
        vault_id = vault.id

        repo = BaseRepository(Vault, db_session)
        assert repo.delete_by_id(vault_id) is True
        db_session.commit()
        assert repo.get_by_id(vault_id) is None

    def test_delete_nonexistent_returns_false(self, db_session) -> None:
        repo = BaseRepository(Vault, db_session)
        assert repo.delete_by_id("nonexistent-id") is False

    def test_exists(self, db_session) -> None:
        vault = Vault(name="E", salt="s", verify_hash="h", algorithm_version=1)
        db_session.add(vault)
        db_session.commit()

        repo = BaseRepository(Vault, db_session)
        assert repo.exists(vault.id) is True
        assert repo.exists("nope") is False


class TestVaultRepository:
    def test_get_first(self, db_session) -> None:
        repo = VaultRepository(db_session)
        assert repo.get_first() is None

        db_session.add(Vault(name="V", salt="s", verify_hash="h", algorithm_version=1))
        db_session.commit()
        assert repo.get_first() is not None

    def test_get_by_name(self, db_session) -> None:
        repo = VaultRepository(db_session)
        db_session.add(Vault(name="MyVault", salt="s", verify_hash="h", algorithm_version=1))
        db_session.commit()

        assert repo.get_by_name("MyVault") is not None
        assert repo.get_by_name("Nope") is None

    def test_mark_unlocked(self, db_session) -> None:
        vault = Vault(name="V", salt="s", verify_hash="h", is_locked=True, algorithm_version=1)
        db_session.add(vault)
        db_session.commit()

        repo = VaultRepository(db_session)
        repo.mark_unlocked(vault.id)
        db_session.commit()

        updated = repo.get_by_id(vault.id)
        assert updated.is_locked is False
        assert updated.last_unlocked_at is not None

    def test_mark_locked(self, db_session) -> None:
        vault = Vault(name="V", salt="s", verify_hash="h", is_locked=False, algorithm_version=1)
        db_session.add(vault)
        db_session.commit()

        repo = VaultRepository(db_session)
        repo.mark_locked(vault.id)
        db_session.commit()

        updated = repo.get_by_id(vault.id)
        assert updated.is_locked is True


class TestVaultModel:
    def test_vault_creation(self, vault_with_key) -> None:
        vault, vault_key = vault_with_key
        assert vault.id is not None
        assert vault.name == "Test Vault"
        assert vault.is_locked is False
        assert len(vault_key) == 32

    def test_vault_with_password_entries(self, db_session, vault_with_key) -> None:
        vault, vault_key = vault_with_key
        password = Password(
            vault_id=vault.id,
            title_enc="encrypted_title",
            username_enc="encrypted_user",
            password_enc="encrypted_pass",
            password_hash="hash",
        )
        db_session.add(password)
        db_session.commit()

        fetched = db_session.get(Vault, vault.id)
        assert len(fetched.passwords) == 1

    def test_vault_with_notes(self, db_session, vault_with_key) -> None:
        vault, vault_key = vault_with_key
        note = SecureNote(
            vault_id=vault.id,
            title_enc="encrypted",
            content_enc="encrypted",
        )
        db_session.add(note)
        db_session.commit()

        fetched = db_session.get(Vault, vault.id)
        assert len(fetched.notes) == 1


class TestMasterPassword:
    def test_create_and_verify(self) -> None:
        vault_key, salt_hex, verify_hash = create_master_password("MySecureP@ssw0rd!")
        from app.authentication.master_password import verify_master_password

        result = verify_master_password("MySecureP@ssw0rd!", salt_hex, verify_hash)
        assert result == vault_key

    def test_wrong_password_fails(self) -> None:
        _, salt_hex, verify_hash = create_master_password("CorrectPassword")
        from app.authentication.master_password import verify_master_password
        from app.core.exceptions import InvalidMasterPasswordError

        with pytest.raises(InvalidMasterPasswordError):
            verify_master_password("WrongPassword", salt_hex, verify_hash)

    def test_change_password(self) -> None:
        from app.authentication.master_password import change_master_password

        vault_key, salt_hex, verify_hash = create_master_password("OldP@ss123!")
        new_key, new_salt, new_hash = change_master_password(
            "OldP@ss123!", "NewP@ss456!", salt_hex, verify_hash
        )
        assert new_key != vault_key
        assert len(new_key) == 32
