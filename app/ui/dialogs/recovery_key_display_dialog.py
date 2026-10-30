"""Recovery key display dialog shown after vault creation."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from app.core.constants import APP_NAME

_NUM_WORDS = 12


class RecoveryKeyDisplayDialog(QDialog):
    """Displays the 12-word recovery key after vault creation."""

    def __init__(self, words: list[str], parent=None) -> None:
        super().__init__(parent)
        self._words = words
        self.setWindowTitle(f"{APP_NAME} - Recovery Key")
        self.setFixedSize(500, 460)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setStyleSheet("QDialog { background-color: #02315F; }")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(32, 24, 32, 24)

        title = QLabel("Your Recovery Key")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #F59E0B;")
        layout.addWidget(title)

        warning = QLabel(
            "Write down these 12 words and store them safely.\n"
            "This is the ONLY way to recover your vault if you forget your master password."
        )
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #FF6B6B; font-size: 11px; font-weight: bold;")
        layout.addWidget(warning)

        layout.addSpacing(6)

        grid = QFrame()
        grid.setStyleSheet(
            "QFrame { background: #0362A6; border: 1px solid #2095CB; border-radius: 8px; padding: 12px; }"
        )
        grid_layout = QHBoxLayout(grid)
        grid_layout.setContentsMargins(18, 14, 18, 14)
        grid_layout.setSpacing(32)

        for col in range(3):
            col_layout = QVBoxLayout()
            col_layout.setSpacing(10)
            for row in range(4):
                idx = col * 4 + row
                word_label = QLabel(f"{idx + 1:>2}. {self._words[idx]}")
                word_label.setFont(QFont("Consolas", 12))
                word_label.setStyleSheet("color: white; background: transparent;")
                col_layout.addWidget(word_label)
            grid_layout.addLayout(col_layout)

        layout.addWidget(grid)

        layout.addSpacing(6)

        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.setMinimumHeight(38)
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setStyleSheet(
            "QPushButton { background: #0362A6; color: #ddd; border: 1px solid #2095CB; "
            "border-radius: 6px; font-size: 12px; }"
            "QPushButton:hover { background: #C19E56; color: white; }"
        )
        copy_btn.clicked.connect(self._copy_to_clipboard)
        layout.addWidget(copy_btn)

        self._copy_status = QLabel()
        self._copy_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._copy_status.setStyleSheet("color: #10B981; font-size: 10px;")
        self._copy_status.hide()
        layout.addWidget(self._copy_status)

        done_btn = QPushButton("I've Saved My Recovery Key")
        done_btn.setMinimumHeight(42)
        done_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        done_btn.setStyleSheet(
            "QPushButton { background: #3B82F6; color: white; border: none; "
            "border-radius: 6px; font-size: 13px; font-weight: bold; }"
            "QPushButton:hover { background: #2563EB; }"
        )
        done_btn.clicked.connect(self.accept)
        layout.addWidget(done_btn)

    def _copy_to_clipboard(self) -> None:
        passphrase = " ".join(self._words)
        QApplication.clipboard().setText(passphrase)
        self._copy_status.setText("Recovery key copied to clipboard")
        self._copy_status.show()

    def get_words(self) -> list[str]:
        return self._words
