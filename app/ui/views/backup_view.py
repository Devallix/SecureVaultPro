"""Backup management view."""

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class BackupView(QWidget):
    """Backup management view."""

    backup_requested = Signal()
    restore_requested = Signal(str)
    delete_backup_requested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    @staticmethod
    def _theme_colors():
        from app.core.config import AppConfig
        is_dark = AppConfig().get("appearance.theme", "dark") == "dark"
        if is_dark:
            return {
                "accent": "#06B6D4",
                "text": "#e0e0e0",
                "text_muted": "#94A3B8",
            }
        else:
            return {
                "accent": "#0891B2",
                "text": "#1a1a2e",
                "text_muted": "#64748B",
            }

    def refresh_theme(self) -> None:
        C = self._theme_colors()
        self._title.setStyleSheet(f"color: {C['accent']}; font-size: 18px; font-weight: bold;")

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        self._title = QLabel("Backups")
        self._title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self._title.setStyleSheet("color: #06B6D4;")
        header.addWidget(self._title)
        header.addStretch()

        backup_btn = QPushButton("+ Create Backup")
        backup_btn.setStyleSheet(
            "QPushButton { background: #06B6D4; color: #1a1a2e; border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #0891B2; }"
        )
        backup_btn.clicked.connect(self.backup_requested.emit)
        header.addWidget(backup_btn)
        layout.addLayout(header)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Filename", "Size", "Created", "Actions"])
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setStyleSheet("QTableWidget { background: #1D263F; }")
        layout.addWidget(self._table)

    def update_backups(self, backups: list[dict]) -> None:
        self._table.setRowCount(len(backups))
        for i, b in enumerate(backups):
            self._table.setItem(i, 0, QTableWidgetItem(b.get("filename", "")))
            self._table.setItem(i, 1, QTableWidgetItem(str(b.get("size", 0))))
            self._table.setItem(i, 2, QTableWidgetItem(b.get("created_at", "")[:19]))

            filepath = b.get("path", b.get("filename", ""))

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)

            restore_btn = QPushButton("Restore")
            restore_btn.setFixedHeight(24)
            restore_btn.setStyleSheet(
                "QPushButton { background: #10B981; color: white; border: none; border-radius: 4px; padding: 2px 12px; font-size: 11px; }"
                "QPushButton:hover { background: #059669; }"
            )
            restore_btn.clicked.connect(lambda _, fp=filepath: self.restore_requested.emit(fp))
            action_layout.addWidget(restore_btn)

            delete_btn = QPushButton("Delete")
            delete_btn.setFixedHeight(24)
            delete_btn.setStyleSheet(
                "QPushButton { background: #EF4444; color: white; border: none; border-radius: 4px; padding: 2px 12px; font-size: 11px; }"
                "QPushButton:hover { background: #DC2626; }"
            )
            delete_btn.clicked.connect(lambda _, fp=filepath: self.delete_backup_requested.emit(fp))
            action_layout.addWidget(delete_btn)

            self._table.setCellWidget(i, 3, action_widget)
