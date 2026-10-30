"""Digital identity view with table-left and preview-right layout."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

TABLE_BG = "#1D263F"


class DigitalIdentityView(QWidget):
    """Digital identity view with table on left and preview panel on right."""

    add_ssh_key = Signal()
    add_api_key = Signal()
    add_licence = Signal()
    delete_ssh_key = Signal(str)
    delete_api_key = Signal(str)
    delete_licence = Signal(str)
    ssh_key_selected = Signal(str)
    api_key_selected = Signal(str)
    licence_selected = Signal(str)
    copy_ssh_field = Signal(str, str)
    copy_api_field = Signal(str, str)
    copy_licence_field = Signal(str, str)
    edit_ssh_key = Signal(str, dict)
    edit_api_key = Signal(str, dict)
    edit_licence = Signal(str, dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._current_id: str | None = None
        self._current_type: str | None = None  # "ssh", "api", "licence"
        self._current_data: dict = {}
        self._build_ui()

    @staticmethod
    def _theme_colors():
        from app.core.config import AppConfig
        is_dark = AppConfig().get("appearance.theme", "dark") == "dark"
        if is_dark:
            return {
                "accent": "#A78BFA",
                "text": "#e0e0e0",
                "text_muted": "#94A3B8",
            }
        else:
            return {
                "accent": "#8B5CF6",
                "text": "#1a1a2e",
                "text_muted": "#64748B",
            }

    def refresh_theme(self) -> None:
        C = self._theme_colors()
        self._title.setStyleSheet(f"color: {C['accent']}; font-size: 18px; font-weight: bold;")
        self._ssh_title.setStyleSheet(f"color: {C['accent']};")
        self._api_title.setStyleSheet(f"color: {C['accent']};")
        self._licence_title.setStyleSheet(f"color: {C['accent']};")

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self._title = QLabel("Digital Identity")
        self._title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self._title.setStyleSheet("color: #A78BFA;")
        layout.addWidget(self._title)

        tabs = QTabWidget()
        tabs.setStyleSheet(
            "QTabBar::tab { padding: 8px 16px; border: none; border-bottom: 2px solid transparent; }"
            "QTabBar::tab:selected { color: #A78BFA; border-bottom: 2px solid #A78BFA; }"
        )
        tabs.addTab(self._build_ssh_tab(), "SSH Keys")
        tabs.addTab(self._build_api_tab(), "API Keys")
        tabs.addTab(self._build_licence_tab(), "Software Licences")
        tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(tabs)

    def _build_ssh_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        add_btn = QPushButton("+ Add SSH Key")
        add_btn.setStyleSheet(
            "QPushButton { background: #A78BFA; color: #1a1a2e; border: none; border-radius: 6px; padding: 6px 14px; font-weight: bold; }"
            "QPushButton:hover { background: #8B5CF6; }"
        )
        add_btn.clicked.connect(self.add_ssh_key.emit)
        btn_row.addWidget(add_btn)
        del_btn = QPushButton("Delete Selected")
        del_btn.setStyleSheet(
            "QPushButton { background: #EF4444; color: white; border: none; border-radius: 6px; padding: 6px 14px; }"
            "QPushButton:hover { background: #DC2626; }"
        )
        del_btn.clicked.connect(self._delete_selected_ssh)
        btn_row.addWidget(del_btn)
        layout.addLayout(btn_row)

        content = QHBoxLayout()
        content.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(0)

        self._ssh_table = self._create_table(["Name", "Type", "Fingerprint", "Last Used"])
        self._ssh_table.cellClicked.connect(lambda r, c: self._on_ssh_row_clicked(r, c))
        left.addWidget(self._ssh_table)
        content.addLayout(left, 3)

        self._ssh_detail = self._build_ssh_detail_panel()
        content.addWidget(self._ssh_detail, 2)

        layout.addLayout(content)
        return w

    def _build_api_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        add_btn = QPushButton("+ Add API Key")
        add_btn.setStyleSheet(
            "QPushButton { background: #A78BFA; color: #1a1a2e; border: none; border-radius: 6px; padding: 6px 14px; font-weight: bold; }"
            "QPushButton:hover { background: #8B5CF6; }"
        )
        add_btn.clicked.connect(self.add_api_key.emit)
        btn_row.addWidget(add_btn)
        del_btn = QPushButton("Delete Selected")
        del_btn.setStyleSheet(
            "QPushButton { background: #EF4444; color: white; border: none; border-radius: 6px; padding: 6px 14px; }"
            "QPushButton:hover { background: #DC2626; }"
        )
        del_btn.clicked.connect(self._delete_selected_api)
        btn_row.addWidget(del_btn)
        layout.addLayout(btn_row)

        content = QHBoxLayout()
        content.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(0)

        self._api_table = self._create_table(["Name", "Service", "Expires", "Last Used"])
        self._api_table.cellClicked.connect(lambda r, c: self._on_api_row_clicked(r, c))
        left.addWidget(self._api_table)
        content.addLayout(left, 3)

        self._api_detail = self._build_api_detail_panel()
        content.addWidget(self._api_detail, 2)

        layout.addLayout(content)
        return w

    def _build_licence_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        add_btn = QPushButton("+ Add Licence")
        add_btn.setStyleSheet(
            "QPushButton { background: #A78BFA; color: #1a1a2e; border: none; border-radius: 6px; padding: 6px 14px; font-weight: bold; }"
            "QPushButton:hover { background: #8B5CF6; }"
        )
        add_btn.clicked.connect(self.add_licence.emit)
        btn_row.addWidget(add_btn)
        del_btn = QPushButton("Delete Selected")
        del_btn.setStyleSheet(
            "QPushButton { background: #EF4444; color: white; border: none; border-radius: 6px; padding: 6px 14px; }"
            "QPushButton:hover { background: #DC2626; }"
        )
        del_btn.clicked.connect(self._delete_selected_licence)
        btn_row.addWidget(del_btn)
        layout.addLayout(btn_row)

        content = QHBoxLayout()
        content.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(0)

        self._licence_table = self._create_table(["Name", "Publisher", "Expires"])
        self._licence_table.cellClicked.connect(lambda r, c: self._on_licence_row_clicked(r, c))
        left.addWidget(self._licence_table)
        content.addLayout(left, 3)

        self._licence_detail = self._build_licence_detail_panel()
        content.addWidget(self._licence_detail, 2)

        layout.addLayout(content)
        return w

    def _create_table(self, headers: list[str]) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setStyleSheet(f"QTableWidget {{ background: {TABLE_BG}; }}")
        return table

    def _build_ssh_detail_panel(self) -> QFrame:
        panel = QFrame()
        panel.setStyleSheet("QFrame { border-radius: 8px; }")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        self._ssh_title = QLabel("Select an SSH key")
        self._ssh_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self._ssh_title.setStyleSheet("color: #A78BFA;")
        header.addWidget(self._ssh_title)
        header.addStretch()
        layout.addLayout(header)

        self._ssh_fields: dict[str, tuple[QLabel, QPushButton | None]] = {}
        for field_label, field_key, has_copy in [
            ("Key Type", "key_type", False),
            ("Fingerprint", "fingerprint", True),
            ("Public Key", "public_key", True),
            ("Private Key", "private_key", True),
        ]:
            row = QHBoxLayout()
            lbl_name = QLabel(field_label)
            lbl_name.setFixedWidth(90)
            lbl_name.setStyleSheet("font-size: 12px; font-weight: 500;")
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
                copy_btn.clicked.connect(lambda _, k=field_key: self._on_copy_ssh(k))
                row.addWidget(copy_btn)

            layout.addLayout(row)
            self._ssh_fields[field_key] = (lbl_val, copy_btn)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self._ssh_edit_btn = QPushButton("Edit")
        self._ssh_edit_btn.setEnabled(False)
        self._ssh_edit_btn.setStyleSheet(
            "QPushButton { background: #F59E0B; color: #1a1a2e; border: none; border-radius: 6px; padding: 6px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #D97706; }"
            "QPushButton:disabled { background: #333; color: #666; }"
        )
        self._ssh_edit_btn.clicked.connect(self._on_edit_ssh)
        btn_row.addWidget(self._ssh_edit_btn)

        self._ssh_delete_btn = QPushButton("Delete")
        self._ssh_delete_btn.setEnabled(False)
        self._ssh_delete_btn.setStyleSheet(
            "QPushButton { background: #EF4444; color: white; border: none; border-radius: 6px; padding: 6px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #DC2626; }"
            "QPushButton:disabled { background: #333; color: #666; }"
        )
        self._ssh_delete_btn.clicked.connect(self._on_delete_ssh)
        btn_row.addWidget(self._ssh_delete_btn)

        layout.addLayout(btn_row)
        layout.addStretch()
        return panel

    def _build_api_detail_panel(self) -> QFrame:
        panel = QFrame()
        panel.setStyleSheet("QFrame { border-radius: 8px; }")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        self._api_title = QLabel("Select an API key")
        self._api_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self._api_title.setStyleSheet("color: #A78BFA;")
        header.addWidget(self._api_title)
        header.addStretch()
        layout.addLayout(header)

        self._api_fields: dict[str, tuple[QLabel, QPushButton | None]] = {}
        for field_label, field_key, has_copy in [
            ("Service", "service", False),
            ("Key Value", "key_value", True),
        ]:
            row = QHBoxLayout()
            lbl_name = QLabel(field_label)
            lbl_name.setFixedWidth(90)
            lbl_name.setStyleSheet("font-size: 12px; font-weight: 500;")
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
                copy_btn.clicked.connect(lambda _, k=field_key: self._on_copy_api(k))
                row.addWidget(copy_btn)

            layout.addLayout(row)
            self._api_fields[field_key] = (lbl_val, copy_btn)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self._api_edit_btn = QPushButton("Edit")
        self._api_edit_btn.setEnabled(False)
        self._api_edit_btn.setStyleSheet(
            "QPushButton { background: #F59E0B; color: #1a1a2e; border: none; border-radius: 6px; padding: 6px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #D97706; }"
            "QPushButton:disabled { background: #333; color: #666; }"
        )
        self._api_edit_btn.clicked.connect(self._on_edit_api)
        btn_row.addWidget(self._api_edit_btn)

        self._api_delete_btn = QPushButton("Delete")
        self._api_delete_btn.setEnabled(False)
        self._api_delete_btn.setStyleSheet(
            "QPushButton { background: #EF4444; color: white; border: none; border-radius: 6px; padding: 6px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #DC2626; }"
            "QPushButton:disabled { background: #333; color: #666; }"
        )
        self._api_delete_btn.clicked.connect(self._on_delete_api)
        btn_row.addWidget(self._api_delete_btn)

        layout.addLayout(btn_row)
        layout.addStretch()
        return panel

    def _build_licence_detail_panel(self) -> QFrame:
        panel = QFrame()
        panel.setStyleSheet("QFrame { border-radius: 8px; }")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        self._licence_title = QLabel("Select a licence")
        self._licence_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self._licence_title.setStyleSheet("color: #A78BFA;")
        header.addWidget(self._licence_title)
        header.addStretch()
        layout.addLayout(header)

        self._licence_fields: dict[str, tuple[QLabel, QPushButton | None]] = {}
        for field_label, field_key, has_copy in [
            ("Publisher", "publisher", False),
            ("Licence Key", "licence_key", True),
        ]:
            row = QHBoxLayout()
            lbl_name = QLabel(field_label)
            lbl_name.setFixedWidth(90)
            lbl_name.setStyleSheet("font-size: 12px; font-weight: 500;")
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
                copy_btn.clicked.connect(lambda _, k=field_key: self._on_copy_licence(k))
                row.addWidget(copy_btn)

            layout.addLayout(row)
            self._licence_fields[field_key] = (lbl_val, copy_btn)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self._licence_edit_btn = QPushButton("Edit")
        self._licence_edit_btn.setEnabled(False)
        self._licence_edit_btn.setStyleSheet(
            "QPushButton { background: #F59E0B; color: #1a1a2e; border: none; border-radius: 6px; padding: 6px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #D97706; }"
            "QPushButton:disabled { background: #333; color: #666; }"
        )
        self._licence_edit_btn.clicked.connect(self._on_edit_licence)
        btn_row.addWidget(self._licence_edit_btn)

        self._licence_delete_btn = QPushButton("Delete")
        self._licence_delete_btn.setEnabled(False)
        self._licence_delete_btn.setStyleSheet(
            "QPushButton { background: #EF4444; color: white; border: none; border-radius: 6px; padding: 6px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #DC2626; }"
            "QPushButton:disabled { background: #333; color: #666; }"
        )
        self._licence_delete_btn.clicked.connect(self._on_delete_licence)
        btn_row.addWidget(self._licence_delete_btn)

        layout.addLayout(btn_row)
        layout.addStretch()
        return panel

    def _on_tab_changed(self, index: int) -> None:
        self._clear_selection()

    def _clear_selection(self) -> None:
        self._current_id = None
        self._current_type = None
        self._current_data = {}
        self._ssh_title.setText("Select an SSH key")
        self._ssh_edit_btn.setEnabled(False)
        self._ssh_delete_btn.setEnabled(False)
        for _, (lbl, _) in self._ssh_fields.items():
            lbl.setText("")
        self._api_title.setText("Select an API key")
        self._api_edit_btn.setEnabled(False)
        self._api_delete_btn.setEnabled(False)
        for _, (lbl, _) in self._api_fields.items():
            lbl.setText("")
        self._licence_title.setText("Select a licence")
        self._licence_edit_btn.setEnabled(False)
        self._licence_delete_btn.setEnabled(False)
        for _, (lbl, _) in self._licence_fields.items():
            lbl.setText("")

    def _on_ssh_row_clicked(self, row: int, col: int) -> None:
        item = self._ssh_table.item(row, 0)
        if item:
            entry_id = item.data(Qt.ItemDataRole.UserRole)
            if entry_id:
                self._current_id = entry_id
                self._current_type = "ssh"
                self._ssh_edit_btn.setEnabled(True)
                self._ssh_delete_btn.setEnabled(True)
                self.ssh_key_selected.emit(entry_id)

    def _on_api_row_clicked(self, row: int, col: int) -> None:
        item = self._api_table.item(row, 0)
        if item:
            entry_id = item.data(Qt.ItemDataRole.UserRole)
            if entry_id:
                self._current_id = entry_id
                self._current_type = "api"
                self._api_edit_btn.setEnabled(True)
                self._api_delete_btn.setEnabled(True)
                self.api_key_selected.emit(entry_id)

    def _on_licence_row_clicked(self, row: int, col: int) -> None:
        item = self._licence_table.item(row, 0)
        if item:
            entry_id = item.data(Qt.ItemDataRole.UserRole)
            if entry_id:
                self._current_id = entry_id
                self._current_type = "licence"
                self._licence_edit_btn.setEnabled(True)
                self._licence_delete_btn.setEnabled(True)
                self.licence_selected.emit(entry_id)

    def _delete_selected_ssh(self) -> None:
        entry_id = self._get_selected_id(self._ssh_table)
        if entry_id:
            reply = QMessageBox.question(
                self, "Delete SSH Key",
                "Are you sure you want to delete this SSH key?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.delete_ssh_key.emit(entry_id)

    def _delete_selected_api(self) -> None:
        entry_id = self._get_selected_id(self._api_table)
        if entry_id:
            reply = QMessageBox.question(
                self, "Delete API Key",
                "Are you sure you want to delete this API key?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.delete_api_key.emit(entry_id)

    def _delete_selected_licence(self) -> None:
        entry_id = self._get_selected_id(self._licence_table)
        if entry_id:
            reply = QMessageBox.question(
                self, "Delete Licence",
                "Are you sure you want to delete this software licence?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.delete_licence.emit(entry_id)

    def _on_copy_ssh(self, field_key: str) -> None:
        if self._current_id:
            self.copy_ssh_field.emit(self._current_id, field_key)

    def _on_copy_api(self, field_key: str) -> None:
        if self._current_id:
            self.copy_api_field.emit(self._current_id, field_key)

    def _on_copy_licence(self, field_key: str) -> None:
        if self._current_id:
            self.copy_licence_field.emit(self._current_id, field_key)

    def _on_edit_ssh(self) -> None:
        if self._current_id:
            self.edit_ssh_key.emit(self._current_id, self._current_data)

    def _on_edit_api(self) -> None:
        if self._current_id:
            self.edit_api_key.emit(self._current_id, self._current_data)

    def _on_edit_licence(self) -> None:
        if self._current_id:
            self.edit_licence.emit(self._current_id, self._current_data)

    def _on_delete_ssh(self) -> None:
        self._delete_selected_ssh()

    def _on_delete_api(self) -> None:
        self._delete_selected_api()

    def _on_delete_licence(self) -> None:
        self._delete_selected_licence()

    def _get_selected_id(self, table: QTableWidget) -> str | None:
        row = table.currentRow()
        if row < 0:
            return None
        item = table.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def update_ssh_keys(self, keys: list[dict]) -> None:
        self._ssh_table.setRowCount(len(keys))
        for i, k in enumerate(keys):
            self._ssh_table.setItem(i, 0, QTableWidgetItem(k.get("name", "")))
            self._ssh_table.setItem(i, 1, QTableWidgetItem(k.get("key_type", "")))
            self._ssh_table.setItem(i, 2, QTableWidgetItem(k.get("fingerprint", "")))
            last = k.get("last_used_at")
            self._ssh_table.setItem(i, 3, QTableWidgetItem(str(last)[:19] if last else ""))
            item = self._ssh_table.item(i, 0)
            if item:
                item.setData(Qt.ItemDataRole.UserRole, k.get("id", ""))

    def update_api_keys(self, keys: list[dict]) -> None:
        self._api_table.setRowCount(len(keys))
        for i, k in enumerate(keys):
            self._api_table.setItem(i, 0, QTableWidgetItem(k.get("name", "")))
            self._api_table.setItem(i, 1, QTableWidgetItem(k.get("service", "")))
            exp = k.get("expires_at")
            self._api_table.setItem(i, 2, QTableWidgetItem(str(exp)[:10] if exp else ""))
            last = k.get("last_used_at")
            self._api_table.setItem(i, 3, QTableWidgetItem(str(last)[:19] if last else ""))
            item = self._api_table.item(i, 0)
            if item:
                item.setData(Qt.ItemDataRole.UserRole, k.get("id", ""))

    def update_licences(self, licences: list[dict]) -> None:
        self._licence_table.setRowCount(len(licences))
        for i, lic in enumerate(licences):
            self._licence_table.setItem(i, 0, QTableWidgetItem(lic.get("name", "")))
            self._licence_table.setItem(i, 1, QTableWidgetItem(lic.get("publisher", "")))
            exp = lic.get("expires_at")
            self._licence_table.setItem(i, 2, QTableWidgetItem(str(exp)[:10] if exp else ""))
            item = self._licence_table.item(i, 0)
            if item:
                item.setData(Qt.ItemDataRole.UserRole, lic.get("id", ""))

    def show_ssh_detail(self, entry: dict) -> None:
        self._current_id = entry.get("id")
        self._current_type = "ssh"
        self._current_data = entry
        self._ssh_title.setText(entry.get("name", "Untitled"))
        self._ssh_edit_btn.setEnabled(True)
        self._ssh_delete_btn.setEnabled(True)
        self._ssh_fields["key_type"][0].setText(entry.get("key_type", ""))
        self._ssh_fields["fingerprint"][0].setText(entry.get("fingerprint", ""))
        self._ssh_fields["public_key"][0].setText(entry.get("public_key", ""))
        self._ssh_fields["private_key"][0].setText(entry.get("private_key", ""))

    def show_api_detail(self, entry: dict) -> None:
        self._current_id = entry.get("id")
        self._current_type = "api"
        self._current_data = entry
        self._api_title.setText(entry.get("name", "Untitled"))
        self._api_edit_btn.setEnabled(True)
        self._api_delete_btn.setEnabled(True)
        self._api_fields["service"][0].setText(entry.get("service", ""))
        self._api_fields["key_value"][0].setText(entry.get("key_value", ""))

    def show_licence_detail(self, entry: dict) -> None:
        self._current_id = entry.get("id")
        self._current_type = "licence"
        self._current_data = entry
        self._licence_title.setText(entry.get("name", "Untitled"))
        self._licence_edit_btn.setEnabled(True)
        self._licence_delete_btn.setEnabled(True)
        self._licence_fields["publisher"][0].setText(entry.get("publisher", ""))
        self._licence_fields["licence_key"][0].setText(entry.get("licence_key", ""))
