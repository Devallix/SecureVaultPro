"""Main ViewModel orchestrating application state."""

from PySide6.QtCore import QObject, Signal

from app.core.session import SessionManager, SessionState


class MainViewModel(QObject):
    """ViewModel for the main application window.

    Signals:
        vault_locked: Emitted when vault is locked.
        vault_unlocked: Emitted when vault is unlocked.
    """

    vault_locked = Signal()
    vault_unlocked = Signal()

    def __init__(self, session: SessionManager, parent=None) -> None:
        super().__init__(parent)
        self._session = session
        self._session.state_changed.connect(self._on_state_changed)

    def _on_state_changed(self, state: SessionState) -> None:
        if state == SessionState.LOCKED:
            self.vault_locked.emit()
        elif state == SessionState.UNLOCKED:
            self.vault_unlocked.emit()
