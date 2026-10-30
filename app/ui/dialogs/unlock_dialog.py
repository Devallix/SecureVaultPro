"""Unlock dialog for vault access with brute-force protection."""

import os

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from app.core.config import AppConfig
from app.core.constants import APP_NAME

LOCKOUT_SECONDS = 120


class UnlockDialog(QDialog):
    """Vault unlock dialog shown before the main window."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} - Unlock Vault")
        self.setFixedSize(440, 390)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setStyleSheet("QDialog { background-color: #02315F; }")

        self._vault_key: bytes | None = None
        self._vault_id: str | None = None

        config = AppConfig()
        self._max_attempts: int = config.get("security.max_login_attempts", 4)
        self._failed_attempts: int = 0
        self._lockout_remaining: int = 0

        self._build_ui()

        self._countdown_timer = QTimer(self)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.timeout.connect(self._tick_countdown)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(40, 24, 40, 24)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        icon_path = os.path.join(base_dir, "resources", "icons", "vault.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(icon_label)

        title = QLabel(APP_NAME)
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #64B4FF;")
        layout.addWidget(title)

        subtitle = QLabel("Enter your master password to unlock")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #ddd; font-size: 13px;")
        layout.addWidget(subtitle)

        layout.addSpacing(6)

        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("Master Password")
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._password_input.setMinimumHeight(42)
        self._password_input.setStyleSheet(
            "QLineEdit { background: #0362A6; border: 1px solid #2095CB; "
            "border-radius: 6px; padding: 8px 12px; color: white; font-size: 14px; }"
            "QLineEdit:disabled { background: #02315F; color: #888; }"
        )
        layout.addWidget(self._password_input)

        self._attempts_label = QLabel("")
        self._attempts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._attempts_label.setStyleSheet("color: #F59E0B; font-size: 12px;")
        self._attempts_label.hide()
        layout.addWidget(self._attempts_label)

        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #FF6B6B; font-size: 12px;")
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error_label.hide()
        layout.addWidget(self._error_label)

        self._unlock_btn = QPushButton("Unlock")
        self._unlock_btn.setMinimumHeight(42)
        self._unlock_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._unlock_btn.setStyleSheet(
            "QPushButton { background: #3B82F6; color: white; border: none; "
            "border-radius: 6px; font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background: #2563EB; }"
            "QPushButton:disabled { background: #02315F; color: #666; }"
        )
        self._unlock_btn.clicked.connect(self._on_unlock)
        layout.addWidget(self._unlock_btn)

        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #F59E0B; border: none; "
            "font-size: 13px; }"
            "QPushButton:hover { color: #D97706; text-decoration: underline; }"
        )
        forgot_btn.clicked.connect(self._on_forgot_password)
        layout.addWidget(forgot_btn)

    def _on_unlock(self) -> None:
        if self._lockout_remaining > 0:
            return

        password = self._password_input.text()
        if not password:
            self._show_error("Please enter your master password.")
            return

        try:
            from app.authentication.master_password import verify_master_password
            from app.database.session_factory import get_session
            from app.models.vault import Vault

            with get_session() as session:
                vault = session.query(Vault).first()
                if vault is None:
                    self._show_error("No vault found. Create one first.")
                    return

                self._vault_id = vault.id
                self._vault_key = verify_master_password(password, vault.salt, vault.verify_hash)

            self.accept()
        except Exception:
            self._failed_attempts += 1
            remaining = self._max_attempts - self._failed_attempts

            if remaining <= 0:
                self._start_lockout()
            else:
                self._show_error("Incorrect master password.")
                self._attempts_label.setText(f"{remaining} attempt{'s' if remaining != 1 else ''} remaining")
                self._attempts_label.show()

    def _start_lockout(self) -> None:
        self._lockout_remaining = LOCKOUT_SECONDS
        self._password_input.setEnabled(False)
        self._unlock_btn.setEnabled(False)
        self._error_label.hide()
        self._update_lockout_display()
        self._countdown_timer.start()

    def _tick_countdown(self) -> None:
        self._lockout_remaining -= 1
        if self._lockout_remaining <= 0:
            self._countdown_timer.stop()
            self._end_lockout()
        else:
            self._update_lockout_display()

    def _update_lockout_display(self) -> None:
        minutes = self._lockout_remaining // 60
        seconds = self._lockout_remaining % 60
        self._attempts_label.setText(
            f"Too many failed attempts. Try again in {minutes}:{seconds:02d}"
        )
        self._attempts_label.setStyleSheet("color: #EF4444; font-size: 12px; font-weight: bold;")
        self._attempts_label.show()

    def _end_lockout(self) -> None:
        self._failed_attempts = 0
        self._lockout_remaining = 0
        self._password_input.setEnabled(True)
        self._unlock_btn.setEnabled(True)
        self._password_input.clear()
        self._attempts_label.setText(f"{self._max_attempts} attempts remaining")
        self._attempts_label.setStyleSheet("color: #F59E0B; font-size: 12px;")
        self._attempts_label.show()

    def _on_forgot_password(self) -> None:
        from app.ui.dialogs.recovery_key_entry_dialog import RecoveryKeyEntryDialog

        dialog = RecoveryKeyEntryDialog(self)
        if dialog.exec():
            self._vault_key = dialog.vault_key
            self._vault_id = dialog.vault_id
            self.accept()

    def _show_error(self, message: str) -> None:
        self._error_label.setText(message)
        self._error_label.show()

    def get_password(self) -> str:
        return self._password_input.text()

    @property
    def vault_key(self) -> bytes | None:
        return self._vault_key

    @property
    def vault_id(self) -> str | None:
        return self._vault_id
