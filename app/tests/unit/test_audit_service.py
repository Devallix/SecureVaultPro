"""Tests for AuditService — event logging and retrieval."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.authentication.master_password import create_master_password
from app.database.base import Base
from app.models import Vault
from app.repositories.audit_repository import AuditRepository
from app.services.audit_service import AuditService


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
def audit_service(db_session, vault_with_key):
    vault, vault_key = vault_with_key
    repo = AuditRepository(db_session)
    return AuditService(repo), vault


class TestAuditService:
    def test_log_event(self, db_session, audit_service):
        service, vault = audit_service
        service.log(vault.id, "vault_unlocked", entity_type="vault", entity_id=vault.id)

        entries = service.get_all(vault.id)
        assert len(entries) == 1
        assert entries[0]["action"] == "vault_unlocked"
        assert entries[0]["entity_type"] == "vault"
        assert entries[0]["entity_id"] == vault.id

    def test_get_recent(self, db_session, audit_service):
        service, vault = audit_service
        for i in range(5):
            service.log(vault.id, f"action_{i}", entity_type="password")

        recent = service.get_recent(vault.id, hours=1)
        assert len(recent) == 5
        assert all(e["action"].startswith("action_") for e in recent)
