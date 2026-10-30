"""Enhanced status bar with vault name and lock state."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from app.core.session import SessionManager, SessionState


class EnhancedStatusBar(QWidget):
    """Custom status bar showing vault name and lock state."""

    lock_requested = Signal()

    def __init__(
        self, session: SessionManager, vault_id: str, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._session = session
        self._vault_id = vault_id
        self._vault_name = self._resolve_vault_name()

        self._build_ui()
        self._connect_session()

    # ── Public API ──

    def set_message(self, text: str) -> None:
        """Update the centre message area."""
        self._message_label.setText(text)

    # ── Internals ──

    def _resolve_vault_name(self) -> str:
        try:
            from app.database.session_factory import create_session
            from app.repositories.vault_repository import VaultRepository

            db = create_session()
            try:
                repo = VaultRepository(db)
                vault = repo.get_by_id(self._vault_id)
                return vault.name if vault else "Vault"
            finally:
                db.close()
        except Exception:
            return "Vault"

    def _build_ui(self) -> None:
        self.setFixedHeight(28)
        self.setStyleSheet(
            "EnhancedStatusBar { background: #12122a; border-top: 1px solid #2a2a4a; }"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        self._lock_icon = QLabel("\U0001F513")
        self._lock_icon.setFixedSize(20, 20)
        self._lock_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lock_icon.setStyleSheet("font-size: 13px; background: transparent;")
        layout.addWidget(self._lock_icon)

        self._vault_label = QLabel(self._vault_name)
        self._vault_label.setStyleSheet(
            "color: #64B4FF; font-size: 11px; font-weight: bold; background: transparent;"
        )
        layout.addWidget(self._vault_label)

        layout.addStretch()

        self._message_label = QLabel("")
        self._message_label.setStyleSheet("color: #888; font-size: 11px; background: transparent;")
        layout.addWidget(self._message_label)

        layout.addStretch()

        self._powered_label = QLabel("Powered by Devallix")
        self._powered_label.setStyleSheet(
            "color: #C19E56; font-size: 10px; background: transparent; padding-left: 8px;"
        )
        layout.addWidget(self._powered_label)

    def _connect_session(self) -> None:
        self._session.state_changed.connect(self._on_state_changed)

    def _on_state_changed(self, state: SessionState) -> None:
        if state == SessionState.UNLOCKED:
            self._lock_icon.setText("\U0001F512")
            self._lock_icon.setStyleSheet(
                "font-size: 13px; color: #10B981; background: transparent;"
            )
            self._vault_label.setStyleSheet(
                "color: #64B4FF; font-size: 11px; font-weight: bold;"
                " background: transparent;"
            )
        elif state == SessionState.LOCKED:
            self._lock_icon.setText("\U0001F513")
            self._lock_icon.setStyleSheet(
                "font-size: 13px; color: #EF4444; background: transparent;"
            )
