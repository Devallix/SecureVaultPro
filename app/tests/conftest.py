"""Shared test fixtures for SecureVault Pro test suite."""

import pytest

from app.core.app_container import reset_container
from app.core.config import AppConfig


@pytest.fixture(autouse=True)
def reset_app_container():
    """Reset the DI container before each test."""
    reset_container()
    yield
    reset_container()


@pytest.fixture
def app_config():
    """Provide a fresh AppConfig instance."""
    return AppConfig()
