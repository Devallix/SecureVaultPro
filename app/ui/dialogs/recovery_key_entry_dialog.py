"""Recovery key entry dialog for vault recovery."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.constants import APP_NAME

_NUM_WORDS = 12
_COLS = 3


class RecoveryKeyEntryDialog(QDialog):
    """Dialog for entering the 12-word recovery key."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} - Recover Vault")
        self.setFixedSize(620, 340)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.MSWindowsFixedSizeDialogHint)

        self._vault_key: bytes | None = None
        self._inputs: list[QLineEdit] = []

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(24, 16, 24, 16)

        title = QLabel("Recover Your Vault")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #F59E0B;")
        layout.addWidget(title)

        subtitle = QLabel("Enter your 12-word recovery key")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(subtitle)

        layout.addSpacing(4)

        grid_frame = QFrame()
        grid_frame.setStyleSheet(
            "QFrame { background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 8px; padding: 8px; }"
        )
        grid = QGridLayout(grid_frame)
        grid.setSpacing(6)
        grid.setContentsMargins(10, 10, 10, 10)

        input_style = (
            "QLineEdit { background: #2a2a3a; border: 1px solid #444; "
            "border-radius: 4px; padding: 4px 8px; color: white; font-size: 12px; }"
        )
        label_style = "color: #888; font-size: 12px; font-weight: bold; background: transparent;"

        for i in range(_NUM_WORDS):
            row, col = divmod(i, _COLS)
            grid_col = col * 2

            num_label = QLabel(f"{i + 1}.")
            num_label.setStyleSheet(label_style)
            num_label.setFixedWidth(36)
            num_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            grid.addWidget(num_label, row, grid_col)

            entry = QLineEdit()
            entry.setFixedHeight(30)
            entry.setMinimumWidth(120)
            entry.setStyleSheet(input_style)
            entry.setPlaceholderText(f"word {i + 1}")
            self._inputs.append(entry)
            grid.addWidget(entry, row, grid_col + 1)

        layout.addWidget(grid_frame)

        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #FF6B6B; font-size: 12px;")
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error_label.hide()
        layout.addWidget(self._error_label)

        recover_btn = QPushButton("Recover Vault")
        recover_btn.setMinimumHeight(38)
        recover_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        recover_btn.setStyleSheet(
            "QPushButton { background: #3B82F6; color: white; border: none; "
            "border-radius: 6px; font-size: 13px; font-weight: bold; }"
            "QPushButton:hover { background: #2563EB; }"
        )
        recover_btn.clicked.connect(self._on_recover)
        layout.addWidget(recover_btn)

    def _on_recover(self) -> None:
        words = [inp.text().strip().lower() for inp in self._inputs]

        if any(w == "" for w in words):
            self._show_error("Please fill in all 12 words.")
            return

        if not all(w.isalpha() for w in words):
            self._show_error("Recovery key words should only contain letters.")
            return

        try:
            from app.database.session_factory import create_session
            from app.models.vault import Vault
            from app.repositories.recovery_key_repository import RecoveryKeyRepository
            from app.services.recovery_key_service import RecoveryKeyService

            session = create_session()
            try:
                vault = session.query(Vault).first()
                if vault is None:
                    self._show_error("No vault found.")
                    return

                vault_id = vault.id
                vault_salt = vault.salt
            finally:
                session.close()

            session = create_session()
            try:
                repo = RecoveryKeyRepository(session)
                service = RecoveryKeyService(repo)
                self._vault_key = service.verify_and_unlock(words, vault_id, vault_salt)
                self._vault_id = vault_id
            finally:
                session.close()

            self.accept()
        except Exception as e:
            self._show_error(str(e))
            self._vault_id = vault_id

            self.accept()
        except Exception as e:
            self._show_error(str(e))

    def _show_error(self, message: str) -> None:
        self._error_label.setText(message)
        self._error_label.show()

    @property
    def vault_key(self) -> bytes | None:
        return self._vault_key

    @property
    def vault_id(self) -> str | None:
        return getattr(self, "_vault_id", None)
