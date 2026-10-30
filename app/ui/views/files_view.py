"""File encryption view."""

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class FilesView(QWidget):
    """File encryption management view."""

    encrypt_requested = Signal(bool)
    encrypt_folder_requested = Signal(bool)
    decrypt_requested = Signal(str)
    delete_requested = Signal(str)
    clear_all_requested = Signal()
    decrypt_all_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    @staticmethod
    def _theme_colors():
        from app.core.config import AppConfig
        is_dark = AppConfig().get("appearance.theme", "dark") == "dark"
        if is_dark:
            return {
                "accent": "#F59E0B",
                "text": "#e0e0e0",
                "text_muted": "#94A3B8",
            }
        else:
            return {
                "accent": "#D97706",
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
        self._title = QLabel("Encrypted Files")
        self._title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self._title.setStyleSheet("color: #F59E0B;")
        header.addWidget(self._title)

        self._count_label = QLabel("0 files")
        self._count_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        header.addWidget(self._count_label)

        header.addStretch()

        self._delete_original_cb = QCheckBox("Delete original after encrypt")
        self._delete_original_cb.setStyleSheet(
            "QCheckBox { font-size: 11px; }"
            "QCheckBox::indicator { width: 14px; height: 14px; }"
        )
        header.addWidget(self._delete_original_cb)

        encrypt_btn = QPushButton("+ Encrypt File")
        encrypt_btn.setStyleSheet(
            "QPushButton { background: #F59E0B; color: #1a1a2e; border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #D97706; }"
        )
        encrypt_btn.clicked.connect(self._on_encrypt_file)
        header.addWidget(encrypt_btn)

        encrypt_folder_btn = QPushButton("+ Encrypt Folder")
        encrypt_folder_btn.setStyleSheet(
            "QPushButton { background: #F59E0B; color: #1a1a2e; border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #D97706; }"
        )
        encrypt_folder_btn.clicked.connect(self._on_encrypt_folder)
        header.addWidget(encrypt_folder_btn)

        clear_all_btn = QPushButton("Clear All")
        clear_all_btn.setStyleSheet(
            "QPushButton { background: #EF4444; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #DC2626; }"
        )
        clear_all_btn.clicked.connect(self._on_clear_all)
        header.addWidget(clear_all_btn)

        decrypt_all_btn = QPushButton("Decrypt All")
        decrypt_all_btn.setStyleSheet(
            "QPushButton { background: #3B82F6; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #2563EB; }"
        )
        decrypt_all_btn.clicked.connect(self._on_decrypt_all)
        header.addWidget(decrypt_all_btn)
        layout.addLayout(header)

        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["#", "File Name", "Size", "Encrypted Date", "Actions"])
        header_view = self._table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        for col in range(1, 5):
            header_view.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)

        self._table.setStyleSheet("QTableWidget { background: #1D263F; }")

        layout.addWidget(self._table)

        self._status_label = QLabel()
        self._status_label.setVisible(False)
        layout.addWidget(self._status_label)

        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(lambda: self._status_label.setVisible(False))

    def _on_encrypt_file(self) -> None:
        self.encrypt_requested.emit(self._delete_original_cb.isChecked())

    def _on_encrypt_folder(self) -> None:
        self.encrypt_folder_requested.emit(self._delete_original_cb.isChecked())

    def _on_clear_all(self) -> None:
        reply = QMessageBox.question(
            self,
            "Clear All Encrypted Files",
            "This will securely delete ALL encrypted files and their metadata.\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.clear_all_requested.emit()

    def _on_decrypt_all(self) -> None:
        reply = QMessageBox.question(
            self,
            "Decrypt All Files",
            "This will decrypt ALL encrypted files to a folder you choose.\nProceed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.decrypt_all_requested.emit()

    def _flash_status(self, message: str, color: str) -> None:
        self._status_label.setText(message)
        self._status_label.setStyleSheet(
            f"color: {color}; font-size: 11px; font-weight: bold; padding: 2px 0;"
        )
        self._status_label.setVisible(True)
        self._status_timer.start(3000)

    def clear_files(self) -> None:
        self._table.setRowCount(0)
        self._count_label.setText("0 files")

    def update_files(self, files: list[dict]) -> None:
        self._count_label.setText(f"{len(files)} file{'s' if len(files) != 1 else ''}")
        self._table.setRowCount(len(files))
        for i, f in enumerate(files):
            num_item = QTableWidgetItem(str(i + 1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(i, 0, num_item)
            self._table.setItem(i, 1, QTableWidgetItem(f.get("original_name", "")))
            size = f.get("file_size", 0)
            if size >= 1024 * 1024:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            elif size >= 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size} B"
            self._table.setItem(i, 2, QTableWidgetItem(size_str))
            created = f.get("created_at")
            self._table.setItem(i, 3, QTableWidgetItem(str(created)[:19] if created else ""))

            file_id = f.get("id", "")
            self._table.item(i, 1).setData(Qt.ItemDataRole.UserRole, file_id)

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(4)

            decrypt_btn = QPushButton("Decrypt")
            decrypt_btn.setFixedHeight(24)
            decrypt_btn.setStyleSheet(
                "QPushButton { background: #3B82F6; color: white; border: none; border-radius: 4px; padding: 2px 8px; font-size: 11px; }"
                "QPushButton:hover { background: #2563EB; }"
            )
            decrypt_btn.clicked.connect(lambda _, fid=file_id: self.decrypt_requested.emit(fid))
            action_layout.addWidget(decrypt_btn)

            delete_btn = QPushButton("Delete")
            delete_btn.setFixedHeight(24)
            delete_btn.setStyleSheet(
                "QPushButton { background: #EF4444; color: white; border: none; border-radius: 4px; padding: 2px 8px; font-size: 11px; }"
                "QPushButton:hover { background: #DC2626; }"
            )
            delete_btn.clicked.connect(lambda _, fid=file_id: self.delete_requested.emit(fid))
            action_layout.addWidget(delete_btn)

            self._table.setCellWidget(i, 4, action_widget)
