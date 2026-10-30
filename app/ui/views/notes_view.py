"""Secure notes view."""

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.markdown_editor import MarkdownEditor


class NotesView(QWidget):
    """Secure notes list and editor view."""

    add_note_requested = Signal()
    save_note_requested = Signal(str, str)
    delete_note_requested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._current_note_id: str | None = None
        self._build_ui()

    @staticmethod
    def _theme_colors():
        from app.core.config import AppConfig
        is_dark = AppConfig().get("appearance.theme", "dark") == "dark"
        if is_dark:
            return {
                "accent": "#10B981",
                "disabled_bg": "#333",
                "disabled_text": "#666",
            }
        else:
            return {
                "accent": "#059669",
                "disabled_bg": "#e8e8ec",
                "disabled_text": "#aaa",
            }

    def refresh_theme(self) -> None:
        C = self._theme_colors()
        self._save_btn.setStyleSheet(
            "QPushButton { background: #10B981; color: white; border: none; border-radius: 6px; padding: 6px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #059669; }"
            f"QPushButton:disabled {{ background: {C['disabled_bg']}; color: {C['disabled_text']}; }}"
        )
        self._delete_btn.setStyleSheet(
            "QPushButton { background: #EF4444; color: white; border: none; border-radius: 6px; padding: 6px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #DC2626; }"
            f"QPushButton:disabled {{ background: {C['disabled_bg']}; color: {C['disabled_text']}; }}"
        )
        self._editor.refresh_theme()

    def _build_ui(self) -> None:
        C = self._theme_colors()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Secure Notes")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C['accent']};")
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("+ New Note")
        add_btn.setStyleSheet(
            "QPushButton { background: #10B981; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #059669; }"
        )
        add_btn.clicked.connect(self.add_note_requested.emit)
        header.addWidget(add_btn)
        layout.addLayout(header)

        content_layout = QHBoxLayout()

        self._list = QListWidget()
        self._list.setFixedWidth(250)
        self._list.setStyleSheet(
            "QListWidget { border-radius: 8px; }"
            "QListWidget::item { padding: 10px; }"
        )
        self._list.currentItemChanged.connect(self._on_note_selected)
        content_layout.addWidget(self._list)

        editor_layout = QVBoxLayout()
        editor_layout.setSpacing(8)

        self._editor = MarkdownEditor()
        self._editor.setPlaceholderText("Select or create a note...")
        editor_layout.addWidget(self._editor)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self._save_btn = QPushButton("Save")
        self._save_btn.setEnabled(False)
        self._save_btn.setStyleSheet(
            "QPushButton { background: #10B981; color: white; border: none; border-radius: 6px; padding: 6px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #059669; }"
            f"QPushButton:disabled {{ background: {C['disabled_bg']}; color: {C['disabled_text']}; }}"
        )
        self._save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(self._save_btn)

        self._delete_btn = QPushButton("Delete")
        self._delete_btn.setEnabled(False)
        self._delete_btn.setStyleSheet(
            "QPushButton { background: #EF4444; color: white; border: none; border-radius: 6px; padding: 6px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #DC2626; }"
            f"QPushButton:disabled {{ background: {C['disabled_bg']}; color: {C['disabled_text']}; }}"
        )
        self._delete_btn.clicked.connect(self._on_delete)
        btn_row.addWidget(self._delete_btn)

        editor_layout.addLayout(btn_row)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet(
            "font-size: 11px; font-weight: bold; padding: 2px 0;"
        )
        self._status_label.setVisible(False)
        editor_layout.addWidget(self._status_label)

        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(lambda: self._status_label.setVisible(False))

        content_layout.addLayout(editor_layout)

        layout.addLayout(content_layout)

    def _on_note_selected(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        if current is None:
            return
        note_id = current.data(Qt.ItemDataRole.UserRole)
        note_text = current.data(Qt.ItemDataRole.UserRole + 1)
        if note_id and note_text is not None:
            self._current_note_id = note_id
            self._editor.setPlainText(str(note_text))
            self._save_btn.setEnabled(True)
            self._delete_btn.setEnabled(True)

    def _on_save(self) -> None:
        if self._current_note_id:
            self.save_note_requested.emit(self._current_note_id, self._editor.toPlainText())
            self._flash_status("Note saved successfully.", "#10B981")

    def _on_delete(self) -> None:
        if not self._current_note_id:
            return
        reply = QMessageBox.question(
            self,
            "Delete Note",
            "Are you sure you want to delete this note?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_note_requested.emit(self._current_note_id)
            self._current_note_id = None
            self._editor.clear()
            self._save_btn.setEnabled(False)
            self._delete_btn.setEnabled(False)
            self._flash_status("Note deleted.", "#EF4444")

    def _flash_status(self, message: str, color: str) -> None:
        self._status_label.setText(message)
        self._status_label.setStyleSheet(
            f"color: {color}; font-size: 11px; font-weight: bold; padding: 2px 0;"
        )
        self._status_label.setVisible(True)
        self._status_timer.start(3000)

    def update_notes(self, notes: list[dict]) -> None:
        """Populate the list with notes."""
        current_id = self._current_note_id
        self._list.clear()
        for note in notes:
            item = QListWidgetItem(note.get("title", "Untitled"))
            item.setData(Qt.ItemDataRole.UserRole, note.get("id", ""))
            item.setData(Qt.ItemDataRole.UserRole + 1, note.get("content", ""))
            self._list.addItem(item)
            if note.get("id") == current_id:
                self._list.setCurrentItem(item)
                self._editor.setPlainText(note.get("content", ""))
