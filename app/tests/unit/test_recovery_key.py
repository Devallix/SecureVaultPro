"""Tests for recovery key generation and verification."""

import pytest

from app.authentication.master_password import create_master_password
from app.authentication.recovery_key import verify_recovery_key
from app.core.exceptions import InvalidMasterPasswordError
from app.database.base import Base
from app.models.recovery_key import RecoveryKey
from app.models.vault import Vault
from app.repositories.recovery_key_repository import RecoveryKeyRepository
from app.security.kdf import derive_key_argon2id
from app.services.recovery_key_service import RecoveryKeyService


@pytest.fixture()
def db_session():
    """Create an in-memory SQLite database and session for each test."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    test_session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = test_session_factory()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture()
def vault(db_session):
    """Create a vault in the test database."""
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
    return vault, salt_hex, vault_key


class TestVerifyRecoveryKey:
    def test_correct_passphrase(self, vault) -> None:
        vault_obj, salt_hex, _ = vault
        words = [
            "soul", "giant", "main", "cake", "flower", "main",
            "chicken", "pattern", "wise", "match", "magic", "cushion",
        ]
        passphrase = " ".join(words)
        vault_salt = bytes.fromhex(salt_hex)
        key_hash = derive_key_argon2id(passphrase.encode("utf-8"), vault_salt, hash_len=32)

        recovery = RecoveryKey(
            vault_id=vault_obj.id,
            key_hash=key_hash.hex(),
            is_used=False,
        )
        assert verify_recovery_key(passphrase, salt_hex, recovery.key_hash) is True

    def test_incorrect_passphrase(self, vault) -> None:
        _, salt_hex, _ = vault
        words = [
            "soul", "giant", "main", "cake", "flower", "main",
            "chicken", "pattern", "wise", "match", "magic", "cushion",
        ]
        passphrase = " ".join(words)
        vault_salt = bytes.fromhex(salt_hex)
        key_hash = derive_key_argon2id(passphrase.encode("utf-8"), vault_salt, hash_len=32)

        recovery = RecoveryKey(
            vault_id="dummy-vault-id",
            key_hash=key_hash.hex(),
            is_used=False,
        )
        assert verify_recovery_key("wrong passphrase here", salt_hex, recovery.key_hash) is False

    def test_case_insensitive(self, vault) -> None:
        _, salt_hex, _ = vault
        words = ["SOUL", "GIANT", "MAIN", "CAKE", "FLOWER", "MAIN",
                 "CHICKEN", "PATTERN", "WISE", "MATCH", "MAGIC", "CUSHION"]
        passphrase = " ".join(words).lower()
        vault_salt = bytes.fromhex(salt_hex)
        key_hash = derive_key_argon2id(passphrase.encode("utf-8"), vault_salt, hash_len=32)

        recovery = RecoveryKey(
            vault_id="dummy-vault-id",
            key_hash=key_hash.hex(),
            is_used=False,
        )
        assert verify_recovery_key(passphrase, salt_hex, recovery.key_hash) is True


class TestRecoveryKeyService:
    def test_generate_and_store(self, db_session, vault) -> None:
        vault_obj, salt_hex, vault_key = vault
        repo = RecoveryKeyRepository(db_session)
        service = RecoveryKeyService(repo)

        words = service.generate_and_store(vault_obj.id, salt_hex, vault_key)
        assert len(words) == 12
        assert all(w.isalpha() for w in words)

        recovery = repo.get_active_by_vault(vault_obj.id)
        assert recovery is not None
        assert recovery.vault_id == vault_obj.id
        assert recovery.is_used is False
        assert recovery.encrypted_vault_key is not None

    def test_verify_and_unlock_returns_original_key(self, db_session, vault) -> None:
        vault_obj, salt_hex, vault_key = vault
        repo = RecoveryKeyRepository(db_session)
        service = RecoveryKeyService(repo)

        words = service.generate_and_store(vault_obj.id, salt_hex, vault_key)

        recovered_key = service.verify_and_unlock(words, vault_obj.id, salt_hex)
        assert recovered_key == vault_key

    def test_verify_and_unlock_wrong_words(self, db_session, vault) -> None:
        vault_obj, salt_hex, vault_key = vault
        repo = RecoveryKeyRepository(db_session)
        service = RecoveryKeyService(repo)

        service.generate_and_store(vault_obj.id, salt_hex, vault_key)

        wrong_words = [
            "wrong", "giant", "main", "cake", "flower", "main",
            "chicken", "pattern", "wise", "match", "magic", "cushion",
        ]
        with pytest.raises(InvalidMasterPasswordError):
            service.verify_and_unlock(wrong_words, vault_obj.id, salt_hex)

    def test_verify_and_unlock_wrong_count(self, db_session, vault) -> None:
        vault_obj, salt_hex, vault_key = vault
        repo = RecoveryKeyRepository(db_session)
        service = RecoveryKeyService(repo)

        service.generate_and_store(vault_obj.id, salt_hex, vault_key)

        with pytest.raises(InvalidMasterPasswordError):
            service.verify_and_unlock(["only", "three", "words"], vault_obj.id, salt_hex)

    def test_verify_and_unlock_no_active_key(self, db_session, vault) -> None:
        vault_obj, salt_hex, vault_key = vault
        repo = RecoveryKeyRepository(db_session)
        service = RecoveryKeyService(repo)

        # No recovery key stored at all
        with pytest.raises(InvalidMasterPasswordError):
            service.verify_and_unlock(
                ["soul", "giant", "main", "cake", "flower", "main",
                 "chicken", "pattern", "wise", "match", "magic", "cushion"],
                vault_obj.id,
                salt_hex,
            )
