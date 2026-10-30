"""Tests for BackupService — create, list, and restore encrypted backups."""

import time

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.authentication.master_password import create_master_password
from app.database.base import Base
from app.models import Vault
from app.services.backup_service import BackupService


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
def backup_env(tmp_path, vault_with_key):
    vault, vault_key = vault_with_key
    db_file = tmp_path / "vault.db"
    db_file.write_bytes(b"fake-database-content")
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    return vault, vault_key, str(db_file), str(backup_dir)


class TestBackupService:
    def test_create_backup(self, tmp_path, backup_env):
        vault, vault_key, db_path, backup_dir = backup_env
        service = BackupService(vault_key, vault.id, db_path, backup_dir)

        result = service.create_backup()

        assert result["filename"].startswith("backup_")
        assert result["filename"].endswith(".db.bak")
        assert result["size"] > 0
        assert result["checksum"] != ""

    def test_list_backups(self, tmp_path, backup_env):
        vault, vault_key, db_path, backup_dir = backup_env
        service = BackupService(vault_key, vault.id, db_path, backup_dir)

        service.create_backup()
        time.sleep(1.1)
        service.create_backup()

        backups = service.list_backups()
        assert len(backups) == 2
        assert all(b["filename"].endswith(".db.bak") for b in backups)

    def test_restore_backup(self, tmp_path, backup_env):
        vault, vault_key, db_path, backup_dir = backup_env
        service = BackupService(vault_key, vault.id, db_path, backup_dir)

        original_content = b"important-vault-data-12345"
        from pathlib import Path

        Path(db_path).write_bytes(original_content)

        result = service.create_backup()
        assert result["size"] > 0

        Path(db_path).write_bytes(b"different-content")

        success = service.restore_backup(result["path"])
        assert success is True

        restored = Path(db_path).read_bytes()
        assert restored == original_content
