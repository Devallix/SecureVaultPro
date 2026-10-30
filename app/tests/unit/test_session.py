"""Tests for session manager lock/unlock lifecycle."""


import pytest

from app.core.session import SessionManager, SessionState


@pytest.fixture()
def session_manager():
    return SessionManager()


class TestSessionManager:
    def test_starts_locked(self, session_manager) -> None:
        assert session_manager.state == SessionState.LOCKED
        assert not session_manager.is_unlocked
        assert session_manager.vault_key is None

    def test_unlock_sets_state(self, session_manager) -> None:
        session_manager.unlock(b"\x00" * 32, "vault-id-1")
        assert session_manager.state == SessionState.UNLOCKED
        assert session_manager.is_unlocked
        assert session_manager.vault_key == b"\x00" * 32
        assert session_manager.vault_id == "vault-id-1"

    def test_unlock_duration(self, session_manager) -> None:
        assert session_manager.unlock_duration is None
        session_manager.unlock(b"\x00" * 32, "v1")
        assert session_manager.unlock_duration is not None
        assert session_manager.unlock_duration >= 0

    def test_lock_clears_key(self, session_manager) -> None:
        session_manager.unlock(b"\x00" * 32, "v1")
        session_manager.lock()
        assert session_manager.state == SessionState.LOCKED
        assert session_manager.vault_key is None
        assert session_manager.vault_id is None
        assert session_manager.unlock_duration is None

    def test_signals_emit(self, session_manager) -> None:
        states = []
        session_manager.state_changed.connect(lambda s: states.append(s))
        session_manager.unlock(b"\x00" * 32, "v1")
        session_manager.lock()
        assert SessionState.UNLOCKED in states
        assert SessionState.LOCKED in states

    def test_unlocked_signal(self, session_manager) -> None:
        fired = []
        session_manager.unlocked.connect(lambda: fired.append(True))
        session_manager.unlock(b"\x00" * 32, "v1")
        assert len(fired) == 1

    def test_get_unlock_duration_str_locked(self, session_manager) -> None:
        assert session_manager.get_unlock_duration_str() == "Locked"

    def test_get_unlock_duration_str_unlocked(self, session_manager) -> None:
        session_manager.unlock(b"\x00" * 32, "v1")
        result = session_manager.get_unlock_duration_str()
        assert result.endswith("s") or result.endswith("m")
