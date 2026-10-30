"""Create vault dialog for first-time setup."""

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


class CreateVaultDialog(QDialog):
    """First-run vault creation wizard."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} - Create Vault")
        self.setFixedSize(470, 440)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setStyleSheet("QDialog { background-color: #02315F; }")

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(40, 30, 40, 30)

        title = QLabel("Create Your Vault")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #64B4FF;")
        layout.addWidget(title)

        subtitle = QLabel("Choose a strong master password. This cannot be recovered.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #ddd; font-size: 11px;")
        layout.addWidget(subtitle)

        layout.addSpacing(6)

        vault_name_label = QLabel("Vault Name")
        vault_name_label.setStyleSheet("color: #ddd; font-size: 11px;")
        layout.addWidget(vault_name_label)

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("My Vault")
        self._name_input.setMinimumHeight(38)
        self._name_input.setStyleSheet(
            "QLineEdit { background: #0362A6; border: 1px solid #2095CB; border-radius: 6px; padding: 8px 12px; color: white; font-size: 13px; }"
        )
        layout.addWidget(self._name_input)

        pw_label = QLabel("Master Password")
        pw_label.setStyleSheet("color: #ddd; font-size: 11px;")
        layout.addWidget(pw_label)

        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("Enter master password")
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._password_input.setMinimumHeight(38)
        self._password_input.setStyleSheet(
            "QLineEdit { background: #0362A6; border: 1px solid #2095CB; border-radius: 6px; padding: 8px 12px; color: white; font-size: 13px; }"
        )
        layout.addWidget(self._password_input)

        confirm_label = QLabel("Confirm Password")
        confirm_label.setStyleSheet("color: #ddd; font-size: 11px;")
        layout.addWidget(confirm_label)

        self._confirm_input = QLineEdit()
        self._confirm_input.setPlaceholderText("Confirm master password")
        self._confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._confirm_input.setMinimumHeight(38)
        self._confirm_input.setStyleSheet(
            "QLineEdit { background: #0362A6; border: 1px solid #2095CB; border-radius: 6px; padding: 8px 12px; color: white; font-size: 13px; }"
        )
        layout.addWidget(self._confirm_input)

        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #FF6B6B; font-size: 10px;")
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error_label.hide()
        layout.addWidget(self._error_label)

        create_btn = QPushButton("Create Vault")
        create_btn.setMinimumHeight(44)
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.setStyleSheet(
            "QPushButton { background: #3B82F6; color: white; border: none; "
            "border-radius: 6px; font-size: 13px; font-weight: bold; }"
            "QPushButton:hover { background: #2563EB; }"
        )
        create_btn.clicked.connect(self._on_create)
        layout.addWidget(create_btn)

    def _on_create(self) -> None:
        password = self._password_input.text()
        confirm = self._confirm_input.text()

        if len(password) < 8:
            self._show_error("Password must be at least 8 characters.")
            return
        if password != confirm:
            self._show_error("Passwords do not match.")
            return

        self.accept()

    def _show_error(self, message: str) -> None:
        self._error_label.setText(message)
        self._error_label.show()

    def get_data(self) -> tuple[str, str]:
        return self._name_input.text().strip() or "My Vault", self._password_input.text()
