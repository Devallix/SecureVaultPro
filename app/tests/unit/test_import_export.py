"""Tests for ImportExportService — CSV and JSON export/import."""

import csv
import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.authentication.master_password import create_master_password
from app.database.base import Base
from app.models import Vault
from app.repositories.password_repository import PasswordRepository
from app.services.import_export_service import ImportExportService
from app.services.password_service import PasswordService


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
def services(db_session, vault_with_key):
    vault, vault_key = vault_with_key
    pw_repo = PasswordRepository(db_session)
    pw_service = PasswordService(vault_key, pw_repo, db_session)
    ie_service = ImportExportService(vault_key, pw_service, None)
    return ie_service, pw_service, vault


class TestImportExportService:
    def test_export_csv(self, tmp_path, services):
        ie_service, pw_service, vault = services
        pw_service.create_password(vault.id, "Site A", "user1", "pass1", url="https://a.com", notes="n1")
        pw_service.create_password(vault.id, "Site B", "user2", "pass2", url="https://b.com", notes="n2")

        out_path = str(tmp_path / "export.csv")
        count = ie_service.export_passwords_csv(vault.id, out_path)

        assert count == 2
        with open(out_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["title"] == "Site A"
        assert rows[1]["password"] == "pass2"

    def test_import_csv(self, tmp_path, services):
        ie_service, pw_service, vault = services

        csv_path = str(tmp_path / "import.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "username", "password", "url", "notes"])
            writer.writeheader()
            writer.writerow({"title": "Imported A", "username": "u1", "password": "p1", "url": "", "notes": ""})
            writer.writerow({"title": "Imported B", "username": "u2", "password": "p2", "url": "", "notes": ""})

        count = ie_service.import_passwords_csv(vault.id, csv_path)
        assert count == 2

        all_pw = pw_service.get_all_passwords(vault.id)
        titles = {p["title"] for p in all_pw}
        assert "Imported A" in titles
        assert "Imported B" in titles

    def test_export_json(self, tmp_path, services):
        ie_service, pw_service, vault = services
        pw_service.create_password(vault.id, "JSON Entry", "juser", "jpass")

        out_path = str(tmp_path / "export.json")
        count = ie_service.export_passwords_json(vault.id, out_path)

        assert count == 1
        with open(out_path, encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["title"] == "JSON Entry"
        assert data[0]["password"] == "jpass"
