"""Tests for FileService — file encrypt/decrypt, listing, deletion."""

from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.authentication.master_password import create_master_password
from app.database.base import Base
from app.models import Vault
from app.repositories.file_repository import FileRepository
from app.services.file_service import FileService


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
def file_service(db_session, vault_with_key):
    vault, vault_key = vault_with_key
    repo = FileRepository(db_session)
    return FileService(vault_key, repo), vault


class TestFileService:
    def test_encrypt_decrypt_roundtrip(self, tmp_path, db_session, file_service):
        service, vault = file_service

        plaintext = b"Hello, this is a secret file content!"
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        src_file = src_dir / "secret.txt"
        src_file.write_bytes(plaintext)

        enc_dir = tmp_path / "enc"
        enc_dir.mkdir()
        result = service.encrypt_file(vault.id, str(src_file), str(enc_dir))

        assert result["original_name"] == "secret.txt"
        assert result["size"] == len(plaintext)
        assert result["checksum"] != ""

        out_dir = tmp_path / "out"
        out_dir.mkdir()
        output_path = str(out_dir / "decrypted.txt")
        service.decrypt_file(result["id"], output_path)

        assert Path(output_path).read_bytes() == plaintext

    def test_get_files(self, tmp_path, db_session, file_service):
        service, vault = file_service

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        for name in ["a.txt", "b.txt"]:
            (src_dir / name).write_bytes(b"content")

        enc_dir = tmp_path / "enc"
        enc_dir.mkdir()
        service.encrypt_file(vault.id, str(src_dir / "a.txt"), str(enc_dir))
        service.encrypt_file(vault.id, str(src_dir / "b.txt"), str(enc_dir))

        files = service.get_files(vault.id)
        assert len(files) == 2
        names = {f["original_name"] for f in files}
        assert names == {"a.txt", "b.txt"}

    def test_delete_file(self, tmp_path, db_session, file_service):
        service, vault = file_service

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        src_file = src_dir / "delete_me.txt"
        src_file.write_bytes(b"data")

        enc_dir = tmp_path / "enc"
        enc_dir.mkdir()
        result = service.encrypt_file(vault.id, str(src_file), str(enc_dir))

        deleted = service.delete_file(result["id"])
        assert deleted is True
        assert service.get_files(vault.id) == []
