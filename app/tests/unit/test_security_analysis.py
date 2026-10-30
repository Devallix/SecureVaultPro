"""Tests for SecurityAnalysisService — vault health analysis."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.authentication.master_password import create_master_password
from app.database.base import Base
from app.models import Vault
from app.repositories.password_repository import PasswordRepository
from app.services.password_service import PasswordService
from app.services.security_analysis import SecurityAnalysisService


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
def analysis_deps(db_session, vault_with_key):
    vault, vault_key = vault_with_key
    pw_repo = PasswordRepository(db_session)
    pw_service = PasswordService(vault_key, pw_repo, db_session)
    analysis = SecurityAnalysisService(vault_key, pw_repo, pw_service)
    return analysis, pw_service, vault


class TestSecurityAnalysisService:
    def test_analyse_vault_empty(self, analysis_deps):
        analysis, pw_service, vault = analysis_deps

        result = analysis.analyse_vault(vault.id)
        assert result["total_passwords"] == 0
        assert result["health_score"] == 100
        assert result["weak_passwords"] == []
        assert result["recommendations"] == []

    def test_analyse_vault_with_weak(self, analysis_deps):
        analysis, pw_service, vault = analysis_deps
        pw_service.create_password(vault.id, "Weak Account", "user", "abc")

        result = analysis.analyse_vault(vault.id)
        assert result["total_passwords"] == 1
        assert len(result["weak_passwords"]) == 1
        assert result["weak_passwords"][0]["title"] == "Weak Account"
        assert result["health_score"] < 100
        assert len(result["recommendations"]) > 0
