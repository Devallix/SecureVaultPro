"""Category manager dialog for creating, renaming, and deleting categories."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.core.constants import APP_NAME


class CategoryManagerDialog(QDialog):
    """Dialog for managing password categories."""

    categories_changed = Signal()

    def __init__(self, categories: list[dict], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} - Manage Categories")
        self.setFixedSize(400, 420)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self._categories = list(categories)
        self._build_ui()
        self._populate_list()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("Manage Categories")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #64B4FF;")
        layout.addWidget(title)

        self._list = QListWidget()
        self._list.setStyleSheet(
            "QListWidget { background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 6px; color: #e0e0e0; }"
            "QListWidget::item { padding: 8px 12px; }"
            "QListWidget::item:selected { background: #2a2a4a; }"
        )
        layout.addWidget(self._list)

        add_row = QHBoxLayout()
        add_row.setSpacing(6)
        self._new_input = QLineEdit()
        self._new_input.setPlaceholderText("New category name")
        self._new_input.setMinimumHeight(32)
        self._new_input.setStyleSheet(
            "QLineEdit { background: #2a2a3a; border: 1px solid #444; border-radius: 6px; "
            "padding: 6px 10px; color: white; font-size: 12px; }"
        )
        self._new_input.returnPressed.connect(self._on_add)
        add_row.addWidget(self._new_input, 1)

        add_btn = QPushButton("Add")
        add_btn.setFixedHeight(32)
        add_btn.setStyleSheet(
            "QPushButton { background: #3B82F6; color: white; border: none; border-radius: 6px; padding: 6px 14px; font-weight: bold; }"
            "QPushButton:hover { background: #2563EB; }"
        )
        add_btn.clicked.connect(self._on_add)
        add_row.addWidget(add_btn)
        layout.addLayout(add_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        rename_btn = QPushButton("Rename")
        rename_btn.setFixedHeight(32)
        rename_btn.setStyleSheet(
            "QPushButton { background: #F59E0B; color: #1a1a2e; border: none; border-radius: 6px; padding: 6px 14px; font-weight: bold; }"
            "QPushButton:hover { background: #D97706; }"
        )
        rename_btn.clicked.connect(self._on_rename)
        btn_row.addWidget(rename_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setFixedHeight(32)
        delete_btn.setStyleSheet(
            "QPushButton { background: #EF4444; color: white; border: none; border-radius: 6px; padding: 6px 14px; font-weight: bold; }"
            "QPushButton:hover { background: #DC2626; }"
        )
        delete_btn.clicked.connect(self._on_delete)
        btn_row.addWidget(delete_btn)
        layout.addLayout(btn_row)

        close_btn = QPushButton("Done")
        close_btn.setMinimumHeight(36)
        close_btn.setStyleSheet(
            "QPushButton { background: #333; color: #aaa; border: 1px solid #444; border-radius: 6px; font-size: 12px; }"
            "QPushButton:hover { background: #444; color: white; }"
        )
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _populate_list(self) -> None:
        self._list.clear()
        for cat in self._categories:
            item = QListWidgetItem(cat.get("name", ""))
            item.setData(Qt.ItemDataRole.UserRole, cat.get("id", ""))
            self._list.addItem(item)

    def _on_add(self) -> None:
        name = self._new_input.text().strip()
        if not name:
            return
        if any(c["name"].lower() == name.lower() for c in self._categories):
            return
        self.add_requested.emit(name)
        self._new_input.clear()

    def _on_rename(self) -> None:
        item = self._list.currentItem()
        if item is None:
            return
        cat_id = item.data(Qt.ItemDataRole.UserRole)
        from PySide6.QtWidgets import QInputDialog

        new_name, ok = QInputDialog.getText(self, "Rename Category", "New name:", text=item.text())
        if ok and new_name.strip():
            self.rename_requested.emit(cat_id, new_name.strip())

    def _on_delete(self) -> None:
        item = self._list.currentItem()
        if item is None:
            return
        cat_id = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, "Delete Category",
            f"Delete '{item.text()}'? Passwords in this category will become uncategorized.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(cat_id)

    def update_categories(self, categories: list[dict]) -> None:
        self._categories = list(categories)
        self._populate_list()

    add_requested = Signal(str)
    rename_requested = Signal(str, str)
    delete_requested = Signal(str)
