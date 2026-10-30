"""Audit log view."""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class AuditView(QWidget):
    """Audit log viewer."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    @staticmethod
    def _theme_colors():
        from app.core.config import AppConfig
        is_dark = AppConfig().get("appearance.theme", "dark") == "dark"
        if is_dark:
            return {
                "accent": "#8B5CF6",
                "text": "#e0e0e0",
                "text_muted": "#94A3B8",
            }
        else:
            return {
                "accent": "#7C3AED",
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

        self._title = QLabel("Audit Log")
        self._title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self._title.setStyleSheet("color: #8B5CF6;")
        layout.addWidget(self._title)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Timestamp", "Action", "Entity", "Details"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setStyleSheet("QTableWidget { background: #1D263F; }")

        layout.addWidget(self._table)

    def update_audit_log(self, entries: list[dict]) -> None:
        self._table.setRowCount(len(entries))
        for i, entry in enumerate(entries):
            self._table.setItem(i, 0, QTableWidgetItem(str(entry.get("created_at", ""))[:19]))
            self._table.setItem(i, 1, QTableWidgetItem(entry.get("action", "")))
            self._table.setItem(i, 2, QTableWidgetItem(entry.get("entity_type", "") or ""))
            self._table.setItem(i, 3, QTableWidgetItem(entry.get("entity_id", "") or ""))
