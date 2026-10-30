"""Delete vault confirmation dialog with password verification."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from app.core.constants import APP_NAME


class DeleteVaultDialog(QDialog):
    """Three-step confirmation dialog for permanently deleting a vault."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} - Delete Vault")
        self.setFixedSize(460, 360)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self._confirmed = False
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(30, 24, 30, 24)

        title = QLabel("Delete Vault")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #EF4444;")
        layout.addWidget(title)

        warning = QLabel(
            "This will permanently delete:\n"
            "• All passwords and secure notes\n"
            "• All encrypted files (securely overwritten)\n"
            "• All categories, tags, and audit logs\n"
            "• Your vault and recovery key\n\n"
            "This action CANNOT be undone."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #ccc; font-size: 11px; line-height: 1.4px;")
        layout.addWidget(warning)

        layout.addSpacing(4)

        confirm_label = QLabel('Type "DELETE" to confirm:')
        confirm_label.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(confirm_label)

        self._confirm_input = QLineEdit()
        self._confirm_input.setPlaceholderText("DELETE")
        self._confirm_input.setMinimumHeight(36)
        self._confirm_input.setStyleSheet(
            "QLineEdit { background: #2a2a3a; border: 1px solid #444; border-radius: 6px; "
            "padding: 6px 10px; color: white; font-size: 12px; }"
        )
        self._confirm_input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._confirm_input)

        pw_label = QLabel("Enter your master password:")
        pw_label.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(pw_label)

        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("Master Password")
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._password_input.setMinimumHeight(36)
        self._password_input.setStyleSheet(
            "QLineEdit { background: #2a2a3a; border: 1px solid #444; border-radius: 6px; "
            "padding: 6px 10px; color: white; font-size: 12px; }"
        )
        layout.addWidget(self._password_input)

        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #FF6B6B; font-size: 10px;")
        self._error_label.hide()
        layout.addWidget(self._error_label)

        self._delete_btn = QPushButton("Permanently Delete Vault")
        self._delete_btn.setMinimumHeight(40)
        self._delete_btn.setEnabled(False)
        self._delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._delete_btn.setStyleSheet(
            "QPushButton { background: #991B1B; color: white; border: none; "
            "border-radius: 6px; font-size: 13px; font-weight: bold; }"
            "QPushButton:hover { background: #7F1D1D; }"
            "QPushButton:disabled { background: #333; color: #666; }"
        )
        self._delete_btn.clicked.connect(self._on_delete)
        layout.addWidget(self._delete_btn)

    def _on_text_changed(self, text: str) -> None:
        self._delete_btn.setEnabled(text.strip() == "DELETE")

    def _on_delete(self) -> None:
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
                    self._show_error("No vault found.")
                    return
                verify_master_password(password, vault.salt, vault.verify_hash)

            self._confirmed = True
            self.accept()
        except Exception:
            self._show_error("Incorrect master password.")

    def _show_error(self, message: str) -> None:
        self._error_label.setText(message)
        self._error_label.show()

    @property
    def confirmed(self) -> bool:
        return self._confirmed
