"""Password vault view with list, detail panel, and filters."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class PasswordView(QWidget):
    """Password vault list view with detail panel."""

    password_selected = Signal(str)
    add_requested = Signal()
    generate_requested = Signal()
    export_requested = Signal()
    export_json_requested = Signal()
    import_requested = Signal()
    delete_requested = Signal(str)
    edit_requested = Signal(str, dict)
    toggle_favourite = Signal(str, bool)
    copy_requested = Signal(str, str)
    manage_categories_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._current_id: str | None = None
        self._current_data: dict = {}
        self._build_ui()

    @staticmethod
    def _theme_colors():
        from app.core.config import AppConfig
        is_dark = AppConfig().get("appearance.theme", "dark") == "dark"
        if is_dark:
            return {
                "accent": "#64B4FF",
                "text": "#e0e0e0",
                "text_muted": "#94A3B8",
            }
        else:
            return {
                "accent": "#3B82F6",
                "text": "#1a1a2e",
                "text_muted": "#64748B",
            }

    def refresh_theme(self) -> None:
        C = self._theme_colors()
        self._title.setStyleSheet(f"color: {C['accent']}; font-size: 18px; font-weight: bold;")
        self._detail_title.setStyleSheet(f"color: {C['accent']};")

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        self._title = QLabel("Password Vault")
        self._title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self._title.setStyleSheet("color: #64B4FF;")
        header.addWidget(self._title)
        header.addStretch()

        self._favs_only = QCheckBox("Favourites Only")

        self._favs_only.stateChanged.connect(self._on_filter_changed)
        header.addWidget(self._favs_only)

        self._category_filter = QComboBox()
        self._category_filter.setFixedWidth(160)
        self._category_filter.setPlaceholderText("All Categories")
        self._category_filter.setStyleSheet(
            "QComboBox { border-radius: 6px; padding: 6px 12px; }"
        )
        self._category_filter.currentIndexChanged.connect(self._on_filter_changed)
        header.addWidget(self._category_filter)

        manage_cat_btn = QPushButton("Manage")
        manage_cat_btn.setFixedHeight(30)
        manage_cat_btn.setStyleSheet(
            "QPushButton { border-radius: 4px; padding: 2px 8px; font-size: 10px; }"
        )
        manage_cat_btn.clicked.connect(self.manage_categories_requested.emit)
        header.addWidget(manage_cat_btn)

        add_btn = QPushButton("+ Add")
        add_btn.setStyleSheet(
            "QPushButton { background: #3B82F6; color: white; border: none; border-radius: 6px; padding: 8px 14px; font-weight: bold; }"
            "QPushButton:hover { background: #2563EB; }"
        )
        add_btn.clicked.connect(self.add_requested.emit)
        header.addWidget(add_btn)

        gen_btn = QPushButton("Generate")
        gen_btn.setStyleSheet(
            "QPushButton { background: #8B5CF6; color: white; border: none; border-radius: 6px; padding: 8px 14px; font-size: 12px; }"
            "QPushButton:hover { background: #7C3AED; }"
        )
        gen_btn.clicked.connect(self.generate_requested.emit)
        header.addWidget(gen_btn)

        export_btn = QPushButton("Export")
        export_btn.setStyleSheet(
            "QPushButton { background: #10B981; color: white; border: none; border-radius: 6px; padding: 8px 12px; font-size: 12px; }"
            "QPushButton:hover { background: #059669; }"
        )
        export_btn.clicked.connect(self.export_requested.emit)
        header.addWidget(export_btn)

        export_json_btn = QPushButton("Export JSON")
        export_json_btn.setStyleSheet(
            "QPushButton { background: #14B8A6; color: white; border: none; border-radius: 6px; padding: 8px 12px; font-size: 12px; }"
            "QPushButton:hover { background: #0D9488; }"
        )
        export_json_btn.clicked.connect(self.export_json_requested.emit)
        header.addWidget(export_json_btn)

        import_btn = QPushButton("Import")
        import_btn.setStyleSheet(
            "QPushButton { background: #6366F1; color: white; border: none; border-radius: 6px; padding: 8px 12px; font-size: 12px; }"
            "QPushButton:hover { background: #4F46E5; }"
        )
        import_btn.clicked.connect(self.import_requested.emit)
        header.addWidget(import_btn)

        layout.addLayout(header)

        content = QHBoxLayout()
        content.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(0)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Title", "Username", "URL", "Modified"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)

        self._table.setStyleSheet("QTableWidget { background: #1D263F; }")

        self._table.cellClicked.connect(self._on_row_clicked)
        left.addWidget(self._table)
        content.addLayout(left, 3)

        self._detail = self._build_detail_panel()
        content.addWidget(self._detail, 2)

        layout.addLayout(content)

    def _build_detail_panel(self) -> QFrame:
        panel = QFrame()
        panel.setStyleSheet(
            "QFrame { border-radius: 8px; }"
        )
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        self._detail_title = QLabel("Select a password")
        self._detail_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self._detail_title.setStyleSheet("color: #64B4FF;")
        header.addWidget(self._detail_title)
        header.addStretch()

        self._fav_btn = QPushButton("☆")
        self._fav_btn.setFixedSize(32, 32)
        self._fav_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #F59E0B; border: none; font-size: 20px; }"
        )
        self._fav_btn.clicked.connect(self._on_toggle_favourite)
        header.addWidget(self._fav_btn)
        layout.addLayout(header)

        self._expiry_label = QLabel()
        self._expiry_label.setStyleSheet("color: #F59E0B; font-size: 11px;")
        self._expiry_label.setVisible(False)
        layout.addWidget(self._expiry_label)

        self._detail_fields: dict[str, tuple[QLabel, QPushButton | None]] = {}
        for field_label, field_key, has_copy in [
            ("Username", "username", True),
            ("Password", "password", True),
            ("URL", "url", True),
            ("Notes", "notes", False),
        ]:
            row = QHBoxLayout()
            lbl_name = QLabel(field_label)
            lbl_name.setFixedWidth(70)
            lbl_name.setStyleSheet("font-size: 12px;")
            row.addWidget(lbl_name)

            lbl_val = QLabel("")
            lbl_val.setWordWrap(True)
            lbl_val.setStyleSheet("font-size: 12px;")
            row.addWidget(lbl_val, 1)

            copy_btn = None
            if has_copy:
                copy_btn = QPushButton("Copy")
                copy_btn.setFixedHeight(24)
                copy_btn.setStyleSheet(
                    "QPushButton { border: none; border-radius: 4px; padding: 2px 8px; font-size: 11px; }"
                )
                copy_btn.clicked.connect(lambda _, k=field_key: self._on_copy(k))
                row.addWidget(copy_btn)

            layout.addLayout(row)
            self._detail_fields[field_key] = (lbl_val, copy_btn)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self._edit_btn = QPushButton("Edit")
        self._edit_btn.setEnabled(False)
        self._edit_btn.setStyleSheet(
            "QPushButton { background: #F59E0B; color: #1a1a2e; border: none; border-radius: 6px; padding: 6px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #D97706; }"
            "QPushButton:disabled { background: #333; color: #666; }"
        )
        self._edit_btn.clicked.connect(self._on_edit)
        btn_row.addWidget(self._edit_btn)

        self._delete_btn = QPushButton("Delete")
        self._delete_btn.setEnabled(False)
        self._delete_btn.setStyleSheet(
            "QPushButton { background: #EF4444; color: white; border: none; border-radius: 6px; padding: 6px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #DC2626; }"
            "QPushButton:disabled { background: #333; color: #666; }"
        )
        self._delete_btn.clicked.connect(self._on_delete)
        btn_row.addWidget(self._delete_btn)

        layout.addLayout(btn_row)

        history_label = QLabel("Password History")
        history_label.setStyleSheet("font-size: 12px; margin-top: 8px;")
        layout.addWidget(history_label)

        self._history_text = QTextEdit()
        self._history_text.setReadOnly(True)
        self._history_text.setMaximumHeight(100)
        self._history_text.setPlaceholderText("No history available")
        self._history_text.setStyleSheet(
            "QTextEdit { border-radius: 4px; font-size: 11px; padding: 6px; background: #1D263F; }"
        )
        layout.addWidget(self._history_text)

        layout.addStretch()
        return panel

    def _on_row_clicked(self, row: int, col: int) -> None:
        item = self._table.item(row, 0)
        if item:
            entry_id = item.data(Qt.ItemDataRole.UserRole)
            if entry_id:
                self.password_selected.emit(entry_id)

    def _on_copy(self, field_key: str) -> None:
        if self._current_id:
            self.copy_requested.emit(self._current_id, field_key)

    def _on_toggle_favourite(self) -> None:
        if self._current_id:
            new_val = not self._current_data.get("is_favourite", False)
            self.toggle_favourite.emit(self._current_id, new_val)

    def _on_edit(self) -> None:
        if self._current_id:
            self.edit_requested.emit(self._current_id, self._current_data)

    def _on_delete(self) -> None:
        if self._current_id:
            self.delete_requested.emit(self._current_id)

    def set_categories(self, categories: list[dict]) -> None:
        self._category_filter.blockSignals(True)
        self._category_filter.clear()
        self._category_filter.addItem("All Categories", "")
        for cat in categories:
            self._category_filter.addItem(cat.get("name", ""), cat.get("id", ""))
        self._category_filter.blockSignals(False)

    def _on_filter_changed(self) -> None:
        self.password_selected.emit("__refresh__")

    def get_filter(self) -> dict:
        return {
            "favourites_only": self._favs_only.isChecked(),
            "category_id": self._category_filter.currentData() or "",
        }

    def update_passwords(self, passwords: list[dict]) -> None:
        self._table.setRowCount(len(passwords))
        for i, entry in enumerate(passwords):
            title = entry.get("title", "")
            is_fav = entry.get("is_favourite", False)
            display_title = f"★ {title}" if is_fav else title
            self._table.setItem(i, 0, QTableWidgetItem(display_title))
            self._table.setItem(i, 1, QTableWidgetItem(entry.get("username", "")))
            self._table.setItem(i, 2, QTableWidgetItem(entry.get("url", "")))
            updated = entry.get("updated_at")
            self._table.setItem(i, 3, QTableWidgetItem(str(updated)[:19] if updated else ""))
            self._table.item(i, 0).setData(Qt.ItemDataRole.UserRole, entry.get("id", ""))

    def show_password_detail(self, entry: dict) -> None:
        self._current_id = entry.get("id")
        self._current_data = entry

        self._detail_title.setText(entry.get("title", "Untitled"))
        self._fav_btn.setText("★" if entry.get("is_favourite") else "☆")

        self._detail_fields["username"][0].setText(entry.get("username", ""))
        pw = entry.get("password", "")
        self._detail_fields["password"][0].setText("•" * len(pw))
        self._detail_fields["password"][0]._revealed = False
        self._detail_fields["password"][0]._pw = pw
        self._detail_fields["url"][0].setText(entry.get("url", ""))
        self._detail_fields["notes"][0].setText(entry.get("notes", ""))

        self._edit_btn.setEnabled(True)
        self._delete_btn.setEnabled(True)

        expires = entry.get("expires_at")
        if expires:
            from datetime import datetime

            try:
                exp_dt = datetime.fromisoformat(expires) if isinstance(expires, str) else expires
                days_left = (exp_dt - datetime.now()).days
                if days_left <= 0:
                    self._expiry_label.setText(f"⚠ Expired {abs(days_left)} days ago")
                    self._expiry_label.setStyleSheet("color: #EF4444; font-size: 11px;")
                elif days_left <= 14:
                    self._expiry_label.setText(f"⚠ Expires in {days_left} days")
                    self._expiry_label.setStyleSheet("color: #F59E0B; font-size: 11px;")
                else:
                    self._expiry_label.setText(f"Expires in {days_left} days")
                    self._expiry_label.setStyleSheet("color: #888; font-size: 11px;")
                self._expiry_label.setVisible(True)
            except (ValueError, TypeError):
                self._expiry_label.setVisible(False)
        else:
            self._expiry_label.setVisible(False)

    def show_password_history(self, history: list[dict]) -> None:
        self._history_text.clear()
        if not history:
            self._history_text.setPlaceholderText("No history available")
            return
        lines = []
        for h in history:
            created = h.get("created_at", "")
            lines.append(f"• {str(created)[:19]} — hash: {h.get('password_hash', '')[:16]}...")
        self._history_text.setPlainText("\n".join(lines))

    def reveal_password(self) -> None:
        lbl = self._detail_fields["password"][0]
        if hasattr(lbl, "_revealed"):
            lbl._revealed = not lbl._revealed
            if lbl._revealed:
                lbl.setText(getattr(lbl, "_pw", ""))
            else:
                lbl.setText("•" * len(getattr(lbl, "_pw", "")))
