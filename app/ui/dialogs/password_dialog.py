"""Password add/edit dialog with expiry date support."""

from datetime import datetime

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from app.core.constants import APP_NAME


class PasswordDialog(QDialog):
    """Dialog for creating or editing a password entry."""

    def __init__(self, edit_mode: bool = False, current: dict | None = None, categories: list[dict] | None = None, parent=None) -> None:
        super().__init__(parent)
        self._edit_mode = edit_mode
        self._current = current or {}
        self._categories = categories or []
        self.setWindowTitle(f"{APP_NAME} - {'Edit' if edit_mode else 'Add'} Password")
        self.setFixedSize(480, 620 if edit_mode else 580)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setStyleSheet("QDialog { background-color: #02315F; }")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(32, 28, 32, 28)

        title = QLabel("Edit Password" if self._edit_mode else "Add Password")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #64B4FF;")
        layout.addWidget(title)
        layout.addSpacing(4)

        for label_text, attr_name, placeholder, is_password in [
            ("Title", "_title_input", "Entry title", False),
            ("Username", "_username_input", "Username or email", False),
            ("Password", "_password_input", "Password", True),
            ("URL", "_url_input", "https://...", False),
        ]:
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #ddd; font-size: 11px;")
            lbl.setContentsMargins(0, 4, 0, 0)
            layout.addWidget(lbl)

            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setMinimumHeight(36)
            if is_password and not self._edit_mode:
                inp.setEchoMode(QLineEdit.EchoMode.Password)
            elif is_password and self._edit_mode:
                inp.setPlaceholderText("Leave empty to keep current")
            inp.setStyleSheet(
                "QLineEdit { background: #0362A6; border: 1px solid #2095CB; border-radius: 6px; "
                "padding: 6px 10px; color: white; font-size: 12px; }"
            )
            setattr(self, attr_name, inp)
            layout.addWidget(inp)

        lbl = QLabel("Category")
        lbl.setStyleSheet("color: #ddd; font-size: 11px;")
        lbl.setContentsMargins(0, 4, 0, 0)
        layout.addWidget(lbl)

        self._category_combo = QComboBox()
        self._category_combo.setPlaceholderText("No category")
        self._category_combo.setMinimumHeight(36)
        self._category_combo.setStyleSheet(
            "QComboBox { background: #0362A6; border: 1px solid #2095CB; border-radius: 6px; "
            "padding: 6px 10px; color: white; font-size: 12px; }"
            "QComboBox::drop-down { border: none; }"
            "QComboBox QAbstractItemView { background: #0362A6; color: white; selection-background-color: #2095CB; }"
        )
        self._category_combo.addItem("No category", "")
        for cat in self._categories:
            self._category_combo.addItem(cat.get("name", ""), cat.get("id", ""))
        if self._edit_mode:
            current_cat_id = self._current.get("category_id", "")
            if current_cat_id:
                for i in range(self._category_combo.count()):
                    if self._category_combo.itemData(i) == current_cat_id:
                        self._category_combo.setCurrentIndex(i)
                        break
        layout.addWidget(self._category_combo)

        lbl = QLabel("Notes")
        lbl.setStyleSheet("color: #ddd; font-size: 11px;")
        lbl.setContentsMargins(0, 4, 0, 0)
        layout.addWidget(lbl)
        self._notes_input = QTextEdit()
        self._notes_input.setPlaceholderText("Optional notes")
        self._notes_input.setFixedHeight(70)
        self._notes_input.setStyleSheet(
            "QTextEdit { background: #0362A6; border: 1px solid #2095CB; border-radius: 6px; "
            "padding: 6px 10px; color: white; font-size: 12px; }"
        )
        layout.addWidget(self._notes_input)

        lbl = QLabel("Expiry Date (optional)")
        lbl.setStyleSheet("color: #ddd; font-size: 11px;")
        lbl.setContentsMargins(0, 4, 0, 0)
        layout.addWidget(lbl)

        self._expires_cb = QCheckBox("Set expiry date")
        self._expires_cb.setStyleSheet("QCheckBox { color: #ddd; font-size: 11px; }")
        self._expires_cb.stateChanged.connect(self._on_expiry_toggled)
        layout.addWidget(self._expires_cb)

        self._expires_date = QDateEdit()
        self._expires_date.setCalendarPopup(True)
        self._expires_date.setDate(QDate.currentDate().addDays(90))
        self._expires_date.setEnabled(False)
        self._expires_date.setMinimumHeight(36)
        self._expires_date.setStyleSheet(
            "QDateEdit { background: #0362A6; border: 1px solid #2095CB; border-radius: 6px; "
            "padding: 6px 10px; color: white; font-size: 12px; }"
            "QDateEdit:disabled { background: #02315F; color: #888; border: 1px solid #0362A6; }"
            "QCalendarWidget QWidget { background: #0362A6; color: white; }"
            "QCalendarWidget QToolButton { color: white; }"
            "QCalendarWidget QMenu { background: #0362A6; }"
            "QCalendarWidget QSpinBox { background: #02315F; color: white; }"
            "QCalendarWidget QAbstractItemView:enabled { background: #0362A6; color: white; selection-background-color: #2095CB; }"
            "QCalendarWidget QAbstractItemView:disabled { color: #888; }"
        )
        layout.addWidget(self._expires_date)

        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #FF6B6B; font-size: 10px;")
        self._error_label.hide()
        layout.addWidget(self._error_label)
        layout.addSpacing(4)

        if self._edit_mode:
            self._populate_current()

        save_text = "Save Changes" if self._edit_mode else "Add Password"
        save_btn = QPushButton(save_text)
        save_btn.setMinimumHeight(40)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(
            "QPushButton { background: #3B82F6; color: white; border: none; "
            "border-radius: 6px; font-size: 13px; font-weight: bold; }"
            "QPushButton:hover { background: #2563EB; }"
        )
        save_btn.clicked.connect(self._on_save)
        layout.addWidget(save_btn)

    def _on_expiry_toggled(self, state: int) -> None:
        self._expires_date.setEnabled(state == Qt.CheckState.Checked.value)

    def _populate_current(self) -> None:
        self._title_input.setText(self._current.get("title", ""))
        self._username_input.setText(self._current.get("username", ""))
        self._url_input.setText(self._current.get("url", ""))
        self._notes_input.setPlainText(self._current.get("notes", ""))

        expires = self._current.get("expires_at")
        if expires:
            self._expires_cb.setChecked(True)
            try:
                exp_dt = datetime.fromisoformat(expires) if isinstance(expires, str) else expires
                from PySide6.QtCore import QDate
                self._expires_date.setDate(QDate(exp_dt.year, exp_dt.month, exp_dt.day))
            except (ValueError, TypeError):
                pass

    def _on_save(self) -> None:
        title = self._title_input.text().strip()
        if not title:
            self._show_error("Title is required.")
            return

        password = self._password_input.text()
        if not self._edit_mode and not password:
            self._show_error("Password is required.")
            return

        self.accept()

    def _show_error(self, message: str) -> None:
        self._error_label.setText(message)
        self._error_label.show()

    def get_data(self) -> dict:
        data: dict = {
            "title": self._title_input.text().strip(),
            "username": self._username_input.text().strip(),
            "url": self._url_input.text().strip(),
            "notes": self._notes_input.toPlainText().strip(),
            "category_id": self._category_combo.currentData() or "",
        }
        password = self._password_input.text()
        if password:
            data["password"] = password

        if self._expires_cb.isChecked():
            qdate = self._expires_date.date()
            data["expires_at"] = datetime(qdate.year(), qdate.month(), qdate.day())
        else:
            data["expires_at"] = None

        return data
