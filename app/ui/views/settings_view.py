"""Settings view with real config read/write."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class SettingsView(QWidget):
    """Application settings view wired to AppConfig."""

    setting_changed = Signal(str, object)
    delete_vault_requested = Signal()
    check_updates_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._widgets: dict[str, QWidget] = {}
        self._build_ui()

    @staticmethod
    def _theme_colors():
        from app.core.config import AppConfig
        is_dark = AppConfig().get("appearance.theme", "dark") == "dark"
        if is_dark:
            return {
                "accent": "#3B82F6",
                "input_bg": "#2a2a3a",
                "input_border": "#444",
                "text": "#e0e0e0",
            }
        else:
            return {
                "accent": "#2563EB",
                "input_bg": "#ffffff",
                "input_border": "#c0c0c8",
                "text": "#1a1a2e",
            }

    def refresh_theme(self) -> None:
        C = self._theme_colors()
        theme_w = self._widgets.get("appearance.theme")
        if isinstance(theme_w, QComboBox):
            theme_w.setStyleSheet(
                f"QComboBox {{ background: {C['input_bg']}; border: 1px solid {C['input_border']}; border-radius: 6px; padding: 6px 10px; color: {C['text']}; }}"
                "QComboBox::drop-down { border: none; }"
                f"QComboBox QAbstractItemView {{ background: {C['input_bg']}; border: 1px solid {C['input_border']}; color: {C['text']}; }}"
            )
        crypto_w = self._widgets.get("security.default_crypto_version")
        if isinstance(crypto_w, QComboBox):
            crypto_w.setStyleSheet(
                f"QComboBox {{ background: {C['input_bg']}; border: 1px solid {C['input_border']}; border-radius: 6px; padding: 6px 10px; font-size: 12px; color: {C['text']}; }}"
                "QComboBox::drop-down { border: none; }"
                f"QComboBox QAbstractItemView {{ background: {C['input_bg']}; border: 1px solid {C['input_border']}; color: {C['text']}; }}"
            )

    def _build_ui(self) -> None:
        C = self._theme_colors()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(0)

        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C['accent']};")
        outer.addWidget(title)

        outer.addSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
        )

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(0, 0, 4, 0)
        content_layout.setSpacing(12)

        sections = [
            ("Appearance", [
                ("Theme", "appearance.theme", self._create_theme_selector()),
            ]),
            ("Security", [
                ("Auto-lock timeout (seconds)", "security.auto_lock_timeout",
                 self._create_spinbox(30, 3600, 300)),
                ("Clipboard clear (seconds)", "security.clipboard_clear_seconds",
                 self._create_spinbox(5, 120, 30)),
                ("Lock on minimize", "security.lock_on_minimize", QCheckBox()),
                ("Max login attempts", "security.max_login_attempts",
                 self._create_spinbox(1, 20, 5)),
                ("Lock on screen saver", "security.lock_on_screen_saver", QCheckBox()),
                ("Default crypto version", "security.default_crypto_version",
                 self._create_crypto_selector()),
            ]),
            ("Vault", [
                ("Password history count", "vault.password_history_count",
                 self._create_spinbox(0, 100, 20)),
                ("Password expiry days", "vault.password_expiry_days",
                 self._create_spinbox(1, 365, 90)),
            ]),
            ("Notifications", [
                ("Notifications enabled", "notifications.enabled", QCheckBox()),
                ("Password expiry warning (days)", "notifications.password_expiry_warning_days",
                 self._create_spinbox(1, 90, 14)),
            ]),
            ("Backup", [
                ("Auto-backup", "backup.auto_backup_enabled", QCheckBox()),
                ("Backup interval (hours)", "backup.auto_backup_interval_hours",
                 self._create_spinbox(1, 168, 24)),
                ("Max backup versions", "backup.max_backup_versions",
                 self._create_spinbox(1, 50, 10)),
            ]),
            ("Updates", [
                ("Update endpoint", "updates.endpoint", self._create_endpoint_input()),
                ("Check automatically", "updates.check_enabled", QCheckBox()),
                ("Check for updates", None, self._create_check_button()),
            ]),
        ]

        for section_name, items in sections:
            section = self._create_section(section_name, items)
            content_layout.addWidget(section)

        danger_frame = QFrame()
        danger_frame.setStyleSheet(
            "QFrame { background: transparent; border: 1px solid #EF4444; border-radius: 8px; padding: 12px; }"
        )
        danger_layout = QVBoxLayout(danger_frame)
        danger_layout.setContentsMargins(16, 12, 16, 12)
        danger_layout.setSpacing(8)

        danger_title = QLabel("Danger Zone")
        danger_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        danger_title.setStyleSheet("color: #EF4444;")
        danger_layout.addWidget(danger_title)

        danger_desc = QLabel(
            "Permanently delete your vault and ALL stored data.\n"
            "This includes passwords, notes, encrypted files, and audit logs.\n"
            "This action cannot be undone."
        )
        danger_desc.setWordWrap(True)
        danger_desc.setStyleSheet("font-size: 11px;")
        danger_layout.addWidget(danger_desc)

        delete_btn = QPushButton("Delete Vault")
        delete_btn.setFixedWidth(160)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setStyleSheet(
            "QPushButton { background: #EF4444; color: white; border: none; "
            "border-radius: 6px; padding: 8px 16px; font-weight: bold; font-size: 12px; }"
            "QPushButton:hover { background: #DC2626; }"
        )
        delete_btn.clicked.connect(self.delete_vault_requested.emit)
        danger_layout.addWidget(delete_btn)

        content_layout.addWidget(danger_frame)
        content_layout.addStretch()

        scroll.setWidget(scroll_content)
        outer.addWidget(scroll)
        self.refresh_theme()
    def _create_section(self, title: str, items: list) -> QFrame:
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        frame.setStyleSheet(
            "QFrame#sectionFrame { border-radius: 8px; padding: 12px; }"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        section_label = QLabel(title)
        section_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        section_label.setStyleSheet("color: #64B4FF;")
        layout.addWidget(section_label)

        for item in items:
            label_text, key, widget = item
            if key is not None:
                self._widgets[key] = widget
            row = QHBoxLayout()
            row.setSpacing(12)
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 12px;")
            label.setMinimumWidth(220)
            row.addWidget(label)
            row.addStretch()
            row.addWidget(widget)
            layout.addLayout(row)

            if key is None:
                continue
            if isinstance(widget, QSpinBox):
                widget.valueChanged.connect(lambda val, k=key: self._on_setting_changed(k, val))
            elif isinstance(widget, QCheckBox):
                widget.stateChanged.connect(lambda state, k=key: self._on_setting_changed(k, bool(state)))
            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(lambda text, k=key: self._on_setting_changed(k, text))
            elif isinstance(widget, QLineEdit):
                widget.editingFinished.connect(lambda k=key, w=widget: self._on_setting_changed(k, w.text()))

        return frame

    def _create_theme_selector(self) -> QComboBox:
        combo = QComboBox()
        combo.addItems(["dark", "light"])
        combo.setFixedWidth(160)
        return combo

    def _create_crypto_selector(self) -> QComboBox:
        combo = QComboBox()
        combo.addItems(["v1 AES-GCM", "v2 ChaCha20"])
        combo.setFixedWidth(150)
        return combo

    def _create_spinbox(self, min_val: int, max_val: int, default: int) -> QSpinBox:
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        spin.setFixedWidth(110)
        spin.setStyleSheet(
            "QSpinBox { border-radius: 6px; padding: 6px 10px; font-size: 12px; }"
        )
        return spin

    def _create_endpoint_input(self) -> QLineEdit:
        edit = QLineEdit()
        edit.setPlaceholderText("https://example.com/manifest.json")
        edit.setFixedWidth(320)
        return edit

    def _create_check_button(self) -> QPushButton:
        btn = QPushButton("Check for updates")
        btn.setFixedWidth(160)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton { background: #3B82F6; color: white; border: none; "
            "border-radius: 6px; padding: 8px 16px; font-size: 12px; }"
            "QPushButton:hover { background: #2563EB; }"
            "QPushButton:disabled { background: #9CA3AF; }"
        )
        btn.clicked.connect(self.check_updates_requested.emit)
        return btn

    def _on_setting_changed(self, key: str, value) -> None:
        if key == "security.default_crypto_version" and isinstance(value, str):
            value = 2 if "ChaCha20" in value else 1
        self.setting_changed.emit(key, value)

    def load_from_config(self, config) -> None:
        """Load current values from AppConfig into the UI widgets."""
        theme_w = self._widgets.get("appearance.theme")
        if isinstance(theme_w, QComboBox):
            idx = theme_w.findText(config.get("appearance.theme", "dark"))
            if idx >= 0:
                theme_w.setCurrentIndex(idx)

        crypto_w = self._widgets.get("security.default_crypto_version")
        if isinstance(crypto_w, QComboBox):
            crypto_ver = config.get("security.default_crypto_version", 1)
            idx = 1 if crypto_ver == 2 else 0
            crypto_w.setCurrentIndex(idx)

        endpoint_w = self._widgets.get("updates.endpoint")
        if isinstance(endpoint_w, QLineEdit):
            endpoint_w.setText(config.get("updates.endpoint", ""))

        check_w = self._widgets.get("updates.check_enabled")
        if isinstance(check_w, QCheckBox):
            check_w.setChecked(bool(config.get("updates.check_enabled", True)))

        spin_keys = [
            "security.auto_lock_timeout",
            "security.clipboard_clear_seconds",
            "security.max_login_attempts",
            "vault.password_history_count",
            "vault.password_expiry_days",
            "notifications.password_expiry_warning_days",
            "backup.auto_backup_interval_hours",
            "backup.max_backup_versions",
        ]
        for key in spin_keys:
            w = self._widgets.get(key)
            if isinstance(w, QSpinBox):
                val = config.get(key)
                if val is not None:
                    w.setValue(int(val))

        check_keys = [
            "security.lock_on_minimize",
            "security.lock_on_screen_saver",
            "backup.auto_backup_enabled",
            "notifications.enabled",
        ]
        for key in check_keys:
            w = self._widgets.get(key)
            if isinstance(w, QCheckBox):
                val = config.get(key)
                if val is not None:
                    w.setChecked(bool(val))
