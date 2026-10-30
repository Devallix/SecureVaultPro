"""Session manager for vault lock/unlock state.

Tracks the current authentication session, manages vault keys in memory,
and provides auto-lock functionality via timer events.
"""

import time
from enum import Enum, auto
from typing import Any

from PySide6.QtCore import QObject, QTimer, Signal

from app.core.config import AppConfig
from app.security.secure_memory import lock_memory, secure_zero, unlock_memory


class SessionState(Enum):
    """Vault session states."""

    LOCKED = auto()
    UNLOCKING = auto()
    UNLOCKED = auto()
    LOCKING = auto()


class SessionManager(QObject):
    """Manages the application authentication session.

    Tracks lock state, holds the derived vault key in memory,
    and emits signals on state changes. Provides auto-lock via idle timer.

    Signals:
        state_changed: Emitted when session state changes.
        locked: Emitted when vault is locked.
        unlocked: Emitted when vault is unlocked.
        auto_lock_triggered: Emitted when auto-lock activates.
    """

    state_changed = Signal(SessionState)
    locked = Signal()
    unlocked = Signal()
    auto_lock_triggered = Signal()

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self._state: SessionState = SessionState.LOCKED
        self._vault_key: bytearray | None = None
        self._vault_id: str | None = None
        self._last_activity: float = time.monotonic()
        self._unlock_time: float | None = None

        self._auto_lock_timer = QTimer(self)
        self._auto_lock_timer.timeout.connect(self._on_auto_lock_tick)
        self._auto_lock_timer.setInterval(10_000)  # Check every 10 seconds

        self._config = AppConfig()

    @property
    def state(self) -> SessionState:
        """Current session state."""
        return self._state

    @property
    def is_unlocked(self) -> bool:
        """Whether the vault is currently unlocked."""
        return self._state == SessionState.UNLOCKED

    @property
    def vault_key(self) -> bytearray | None:
        """The derived vault key as a mutable bytearray (only available when unlocked)."""
        return self._vault_key

    @property
    def vault_id(self) -> str | None:
        """The ID of the currently unlocked vault."""
        return self._vault_id

    @property
    def unlock_duration(self) -> float | None:
        """Seconds since vault was unlocked, or None if locked."""
        if self._unlock_time is None:
            return None
        return time.monotonic() - self._unlock_time

    def unlock(self, vault_key: bytes, vault_id: str) -> None:
        """Unlock the vault with the derived key.

        Args:
            vault_id: The vault identifier.
            vault_key: The derived encryption key.
        """
        self._state = SessionState.UNLOCKED
        self._vault_key = bytearray(vault_key)
        lock_memory(self._vault_key)
        self._vault_id = vault_id
        self._unlock_time = time.monotonic()
        self._last_activity = time.monotonic()
        self._start_auto_lock_timer()
        self.state_changed.emit(self._state)
        self.unlocked.emit()

    def lock(self) -> None:
        """Lock the vault, wiping the key from memory."""
        self._state = SessionState.LOCKING
        self.state_changed.emit(self._state)

        if self._vault_key is not None:
            unlock_memory(self._vault_key)
            secure_zero(self._vault_key)
        self._vault_key = None
        self._vault_id = None
        self._unlock_time = None
        self._stop_auto_lock_timer()

        self._state = SessionState.LOCKED
        self.state_changed.emit(self._state)
        self.locked.emit()

    def record_activity(self) -> None:
        """Record user activity to reset the auto-lock timer."""
        self._last_activity = time.monotonic()

    def get_unlock_duration_str(self) -> str:
        """Get a human-readable unlock duration string."""
        duration = self.unlock_duration
        if duration is None:
            return "Locked"
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    def _start_auto_lock_timer(self) -> None:
        """Start the auto-lock idle timer."""
        timeout = self._config.auto_lock_timeout * 1000
        self._auto_lock_timer.setInterval(min(timeout, 10_000))
        self._auto_lock_timer.start()

    def _stop_auto_lock_timer(self) -> None:
        """Stop the auto-lock timer."""
        self._auto_lock_timer.stop()

    def _on_auto_lock_tick(self) -> None:
        """Check if idle timeout has been exceeded."""
        if not self.is_unlocked:
            return

        idle_time = time.monotonic() - self._last_activity
        if idle_time >= self._config.auto_lock_timeout:
            self.auto_lock_triggered.emit()
            self.lock()
