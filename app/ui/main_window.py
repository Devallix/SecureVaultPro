"""Main application window for SecureVault Pro."""

import os

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QAction, QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.constants import APP_NAME, APP_VERSION, WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH
from app.ui.widgets.notification_center import NotificationSeverity
from app.ui.widgets.status_bar_widget import EnhancedStatusBar


class MainWindow(QMainWindow):
    """Primary application window with sidebar, workspace, and details panel."""

    vault_locked = Signal()
    vault_deleted = Signal()

    def __init__(self, vault_key: bytes, vault_id: str, parent=None) -> None:
        super().__init__(parent)
        self._vault_key = vault_key
        self._vault_id = vault_id

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(self._create_lock_icon())
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(1400, 900)

        self._nav_buttons: dict[str, QLabel] = {}
        self._lock_btn: QLabel | None = None
        self._current_nav: str = "dashboard"
        self._session = None
        self._sidebar_collapsed = False
        self._sidebar_anim: QPropertyAnimation | None = None
        self._sidebar_widget: QFrame | None = None
        self._sidebar_version_label: QLabel | None = None

        from app.core.config import AppConfig

        theme = AppConfig().get("appearance.theme", "dark")
        self._theme = theme
        self._setup_stylesheet(theme)
        self._build_ui()
        self._setup_menu_bar()
        self._connect_navigation()
        self._init_services_and_viewmodels()
        from app.ui.themes.theme_manager import ThemeManager

        ThemeManager().apply_theme(theme)

    def closeEvent(self, event) -> None:  # noqa: N802
        if self._session is not None:
            try:
                self._session.commit()
            except Exception:
                self._session.rollback()
            self._session.close()
        super().closeEvent(event)

    @staticmethod
    def _create_lock_icon() -> QIcon:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, "resources", "icons", "vault.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def _load_icon(self, name: str) -> QIcon:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, "resources", "icons", name)
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def _setup_stylesheet(self, theme: str = "dark") -> None:
        if theme == "light":
            _bg = "#f5f5f7"
            _card = "#ffffff"
            _card_border = "#d0d0d8"
            _sidebar_bg = "#e8e8ed"
            _sidebar_border = "#d0d0d8"
            _input_bg = "#ffffff"
            _input_border = "#c0c0c8"
            _text = "#1a1a2e"
            _text_sec = "#555"
            _text_muted = "#888"
            _border = "#d0d0d8"
            _btn_bg = "#e0e0e8"
            _btn_border = "#c0c0c8"
            _btn_hover = "#d0d0d8"
            _btn_pressed = "#c0c0c8"
            _btn_disabled = "#e8e8ec"
            _btn_disabled_text = "#aaa"
            _statusbar_bg = "#e8e8ed"
            _menu_bg = "#ffffff"
            _menu_border = "#d0d0d8"
            _scroll_bg = "#f5f5f7"
            _scroll_handle = "#c0c0c8"
            _header_bg = "#e8e8ed"
            _header_text = "#555"
        else:
            _bg = "#02315F"
            _card = "#0362A6"
            _card_border = "#2095CB"
            _sidebar_bg = "#2095CB"
            _sidebar_border = "#0362A6"
            _input_bg = "#0362A6"
            _input_border = "#2095CB"
            _text = "#e0e0e0"
            _text_sec = "#ddd"
            _text_muted = "#bbb"
            _border = "#2095CB"
            _btn_bg = "#0362A6"
            _btn_border = "#2095CB"
            _btn_hover = "#C19E56"
            _btn_pressed = "#7B98AD"
            _btn_disabled = "#02315F"
            _btn_disabled_text = "#888"
            _statusbar_bg = "#0362A6"
            _menu_bg = "#0362A6"
            _menu_border = "#2095CB"
            _scroll_bg = "#02315F"
            _scroll_handle = "#7B98AD"
            _header_bg = "#0362A6"
            _header_text = "#ddd"

        accent_blue = "#3B82F6"
        accent_green = "#10B981"
        accent_red = "#EF4444"
        accent_amber = "#F59E0B"
        accent_purple = "#8B5CF6"
        accent_cyan = "#06B6D4"

        self.setStyleSheet(
            f"""
            QMainWindow {{ background: {_bg}; }}
            QWidget {{ background: {_bg}; color: {_text}; }}
            QFrame#sidebar {{ background: {_sidebar_bg}; border-right: 1px solid {_sidebar_border}; }}
            QFrame#search_results {{ background: {_card}; border-bottom: 1px solid {_card_border}; }}
            QFrame#topBar {{ border-bottom: 1px solid {_card_border}; background: {_bg}; }}
            QFrame#sectionFrame {{ background: {_card}; border: 1px solid {_card_border}; border-radius: 8px; padding: 12px; }}
            QLabel {{ color: {_text}; background: transparent; }}
            QPushButton {{ background: {_btn_bg}; color: {_text}; border: 1px solid {_btn_border}; border-radius: 6px; padding: 8px 16px; font-size: 12px; }}
            QPushButton:hover {{ background: {_btn_hover}; }}
            QPushButton:pressed {{ background: {_btn_pressed}; }}
            QPushButton:disabled {{ background: {_btn_disabled}; color: {_btn_disabled_text}; border-color: {_btn_disabled}; }}
            QLineEdit {{ background: {_input_bg}; border: 1px solid {_input_border}; border-radius: 6px; padding: 8px 12px; color: {_text}; font-size: 13px; }}
            QLineEdit:focus {{ border-color: #2095CB; }}
            QLineEdit:disabled {{ background: {_btn_disabled}; color: {_btn_disabled_text}; }}
            QTextEdit, QPlainTextEdit {{ background: {_input_bg}; border: 1px solid {_input_border}; border-radius: 6px; color: {_text}; padding: 8px; }}
            QComboBox {{ background: {_input_bg}; border: 1px solid {_input_border}; border-radius: 6px; padding: 6px 12px; color: {_text}; }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
            QComboBox QAbstractItemView {{ background: {_input_bg}; border: 1px solid {_input_border}; color: {_text}; selection-background-color: #2095CB; selection-color: white; }}
            QSpinBox {{ background: {_input_bg}; border: 1px solid {_input_border}; border-radius: 6px; padding: 6px 10px; color: {_text}; }}
            QCheckBox {{ color: {_text}; spacing: 6px; }}
            QRadioButton {{ color: {_text}; spacing: 8px; }}
            QScrollBar:vertical {{ background: {_scroll_bg}; width: 10px; border-radius: 5px; }}
            QScrollBar::handle:vertical {{ background: {_scroll_handle}; border-radius: 5px; min-height: 30px; }}
            QScrollBar::handle:vertical:hover {{ background: {_btn_hover}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
            QTableWidget {{ background: {_card}; border: none; color: {_text}; }}
            QTableWidget::item:selected {{ background: #2095CB; color: white; }}
            QHeaderView::section {{ background: {_header_bg}; color: {_header_text}; border: none; border-bottom: 1px solid {_card_border}; padding: 8px; font-weight: bold; }}
            QListWidget {{ background: {_card}; border: 1px solid {_card_border}; border-radius: 6px; color: {_text}; outline: none; }}
            QListWidget::item {{ border-bottom: 1px solid {_card_border}; }}
            QListWidget::item:selected {{ background: #2095CB; color: white; }}
            QStatusBar {{ background: {_statusbar_bg}; color: white; border-top: 1px solid {_border}; font-size: 11px; }}
            QStatusBar QLabel {{ color: white; }}
            QToolTip {{ background: {_input_bg}; color: {_text}; border: 1px solid {_input_border}; border-radius: 4px; padding: 4px 8px; }}
            QMenu {{ background: {_menu_bg}; border: 1px solid {_menu_border}; border-radius: 6px; padding: 4px; }}
            QMenu::item {{ padding: 6px 24px; border-radius: 4px; color: {_text}; }}
            QMenu::item:selected {{ background: #7B98AD; color: white; }}
            QMenu::item:disabled {{ color: {_btn_disabled_text}; }}
            QMenu::separator {{ height: 1px; background: {_menu_border}; margin: 4px 8px; }}
            QGroupBox {{ border: 1px solid {_card_border}; border-radius: 6px; background: {_card}; margin-top: 12px; padding-top: 16px; font-size: 13px; color: {_text_sec}; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; }}
            QTabWidget::pane {{ border: 1px solid {_card_border}; background: {_card}; border-radius: 6px; }}
            QTabBar::tab {{ background: {_btn_bg}; color: {_text}; border: 1px solid {_btn_border}; padding: 8px 16px; }}
            QTabBar::tab:selected {{ background: {_card}; border-bottom-color: {_card}; }}
            QFrame[style$="styled"] {{ background: {_card}; border: 1px solid {_card_border}; border-radius: 8px; padding: 12px; }}
            QMenuBar {{ background: #0362A6; color: {_text}; border: none; }}
            QMenuBar::item {{ background: transparent; padding: 6px 12px; }}
            QMenuBar::item:selected {{ background: #7B98AD; color: white; }}
            """
        )

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        main_layout.addWidget(sidebar)

        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(0, 0, 0, 0)
        right_panel.setSpacing(0)

        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(0, 0, 12, 0)
        top_bar_layout.setSpacing(0)

        self._search_bar = QLineEdit()
        self._search_bar.setPlaceholderText("Search passwords, notes, files...")
        self._search_bar.setFixedHeight(40)
        self._search_bar.setStyleSheet(
            "QLineEdit { background: transparent; border: none; padding: 8px 16px; font-size: 13px; }"
        )
        self._search_bar.textChanged.connect(self._on_search_text_changed)
        top_bar_layout.addWidget(self._search_bar, 1)

        from app.ui.widgets.notification_center import NotificationCenter

        self._notification_center = NotificationCenter()
        top_bar_layout.addWidget(self._notification_center)

        right_panel.addWidget(top_bar)

        self._search_results_container = QFrame()
        self._search_results_container.setObjectName("search_results")
        self._search_results_layout = QVBoxLayout(self._search_results_container)
        self._search_results_layout.setContentsMargins(200, 0, 0, 0)
        self._search_results_layout.setSpacing(0)
        self._search_results_container.setVisible(False)
        right_panel.addWidget(self._search_results_container)

        self._stack = QStackedWidget()

        from app.ui.views.about_view import AboutView
        from app.ui.views.audit_view import AuditView
        from app.ui.views.backup_view import BackupView
        from app.ui.views.dashboard_view import DashboardView
        from app.ui.views.digital_identity_view import DigitalIdentityView
        from app.ui.views.files_view import FilesView
        from app.ui.views.notes_view import NotesView
        from app.ui.views.password_view import PasswordView
        from app.ui.views.report_view import ReportView
        from app.ui.views.security_view import SecurityView
        from app.ui.views.settings_view import SettingsView

        self._dashboard_view = DashboardView()
        self._password_view = PasswordView()
        self._notes_view = NotesView()
        self._files_view = FilesView()
        self._identity_view = DigitalIdentityView()
        self._security_view = SecurityView()
        self._backup_view = BackupView()
        self._audit_view = AuditView()
        self._report_view = ReportView()
        self._settings_view = SettingsView()
        self._about_view = AboutView()

        self._stack.addWidget(self._dashboard_view)
        self._stack.addWidget(self._password_view)
        self._stack.addWidget(self._notes_view)
        self._stack.addWidget(self._files_view)
        self._stack.addWidget(self._identity_view)
        self._stack.addWidget(self._security_view)
        self._stack.addWidget(self._backup_view)
        self._stack.addWidget(self._audit_view)
        self._stack.addWidget(self._report_view)
        self._stack.addWidget(self._settings_view)
        self._stack.addWidget(self._about_view)

        main_layout.addWidget(self._stack)

        right_panel.addWidget(self._stack)
        main_layout.addLayout(right_panel)

    def _setup_menu_bar(self) -> None:
        menu_bar = QMenuBar(self)
        menu_bar.setStyleSheet("QMenuBar { background: #0362A6; color: white; } QMenuBar::item { padding: 6px 12px; } QMenuBar::item:selected { background: #7B98AD; color: white; }")
        self.setMenuBar(menu_bar)

        help_menu = menu_bar.addMenu("&Help")
        eula_action = QAction("EULA", self)
        eula_action.triggered.connect(self._show_eula)
        help_menu.addAction(eula_action)

        user_guide_action = QAction("User Guide", self)
        user_guide_action.triggered.connect(self._show_user_guide)
        help_menu.addAction(user_guide_action)

    def _show_info_dialog(self, title: str, path: str) -> None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(base_dir, "docs", path)
        from PySide6.QtWidgets import QDialog, QPlainTextEdit, QPushButton, QVBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumSize(700, 500)

        layout = QVBoxLayout(dialog)

        text_edit = QPlainTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet(
            "QPlainTextEdit { background: #16162a; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; font-size: 12px; padding: 16px; border: none; border-radius: 8px; }"
        )
        if os.path.exists(file_path):
            with open(file_path, encoding="utf-8") as f:
                text_edit.setPlainText(f.read())
        else:
            text_edit.setPlainText(f"{path} not found in docs/ directory.")
        layout.addWidget(text_edit)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(
            "QPushButton { background: #3B82F6; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-size: 12px; }"
            "QPushButton:hover { background: #2563EB; }"
        )
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    def _show_eula(self) -> None:
        self._show_info_dialog("End User License Agreement", "EULA.md")

    def _show_user_guide(self) -> None:
        self._show_info_dialog("User Guide", "USER_GUIDE.md")

    def _setup_enhanced_status_bar(self) -> None:
        """Replace the default status bar content with the enhanced version."""
        self._enhanced_status_bar = EnhancedStatusBar(self._session_mgr, self._vault_id)
        self.statusBar().setStyleSheet("QStatusBar::item { border: none; }")
        self.statusBar().addPermanentWidget(self._enhanced_status_bar, 1)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)
        self._sidebar_widget = sidebar

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 16, 10, 16)
        layout.setSpacing(4)

        hamburger = QLabel("☰")
        hamburger.setFont(QFont("Segoe UI", 16))
        hamburger.setCursor(Qt.CursorShape.PointingHandCursor)
        hamburger.setStyleSheet("color: white; background: transparent; padding: 8px 4px 18px 4px;")
        hamburger.mousePressEvent = lambda event: self._toggle_sidebar()
        layout.addWidget(hamburger)

        nav_items = [
            ("Dashboard", "dashboard", "dashboard.png"),
            ("Passwords", "passwords", "password.png"),
            ("Notes", "notes", "notes.png"),
            ("Files", "files", "file.png"),
            ("Digital ID", "identity", "id-card.png"),
            ("Security", "security", "shield.png"),
            ("Backups", "backups", "backup.png"),
            ("Audit Log", "audit", "audit.png"),
            ("Reports", "reports", "report.png"),
            ("Settings", "settings", "settings.png"),
            ("About", "about", "info.png"),
        ]

        is_dark = self._theme == "dark"
        hover_bg = "#C19E56"
        hover_text = "white"
        active_bg = "#7B98AD"
        active_text = "white"
        default_text = "white"

        from PySide6.QtWidgets import QHBoxLayout

        for label, name, icon_file in nav_items:
            icon = self._load_icon(icon_file)
            container = QWidget()
            container.setFixedHeight(38)
            container.setCursor(Qt.CursorShape.PointingHandCursor)
            clayout = QHBoxLayout(container)
            clayout.setContentsMargins(12, 0, 12, 0)
            clayout.setSpacing(10)
            icon_label = QLabel()
            if not icon.isNull():
                icon_label.setPixmap(icon.pixmap(18, 18))
            icon_label.setStyleSheet("background: transparent;")
            text_label = QLabel(label)
            text_label.setStyleSheet(f"color: {default_text}; font-size: 13px; background: transparent;")
            clayout.addWidget(icon_label)
            clayout.addWidget(text_label)
            clayout.addStretch()
            container.setStyleSheet(
                f"QWidget {{ border-radius: 6px; background: transparent; }}"
                f"QWidget:hover {{ background: {hover_bg}; }} QWidget:hover QLabel {{ color: {hover_text}; }}"
            )
            container.mousePressEvent = lambda event, n=name: self._on_nav_clicked(n)
            self._nav_buttons[name] = container
            self._nav_buttons[name + "_text"] = text_label
            self._nav_buttons[name + "_icon"] = icon_label
            layout.addWidget(container)

        self._page_map = {
            "dashboard": 0,
            "passwords": 1,
            "notes": 2,
            "files": 3,
            "identity": 4,
            "security": 5,
            "backups": 6,
            "audit": 7,
            "reports": 8,
            "settings": 9,
            "about": 10,
        }

        layout.addStretch()

        lock_btn = QLabel()
        lock_icon = self._load_icon("lock.png")
        lock_container = QWidget()
        lock_container.setFixedHeight(38)
        lock_container.setCursor(Qt.CursorShape.PointingHandCursor)
        lcl = QHBoxLayout(lock_container)
        lcl.setContentsMargins(12, 0, 12, 0)
        lcl.setSpacing(10)
        if not lock_icon.isNull():
            lock_icon_lbl = QLabel()
            lock_icon_lbl.setPixmap(lock_icon.pixmap(18, 18))
            lock_icon_lbl.setStyleSheet("background: transparent;")
            lcl.addWidget(lock_icon_lbl)
        lock_text = QLabel("Lock Vault")
        lock_text.setStyleSheet("color: #FF6B6B; font-size: 13px; background: transparent;")
        lcl.addWidget(lock_text)
        lcl.addStretch()
        lock_container.setStyleSheet(
            "QWidget { border-radius: 6px; background: transparent; } QWidget:hover { background: #C19E56; } QWidget:hover QLabel { color: white; }"
        )
        self._lock_btn = lock_container
        self._lock_btn_text = lock_text
        layout.addWidget(lock_container)

        version_label = QLabel(f"  v{APP_VERSION}")
        version_label.setStyleSheet("font-size: 10px; padding: 10px 4px; color: white;")
        layout.addWidget(version_label)
        self._sidebar_version_label = version_label

        secure_logo = QLabel()
        secure_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logo_path = os.path.join(base_dir, "resources", "icons", "secure-vault.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled = pixmap.scaled(
                180,
                180,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            secure_logo.setPixmap(scaled)
            secure_logo.setStyleSheet("background: transparent; padding: 6px 0;")
            layout.addWidget(secure_logo)

        return sidebar

    def _toggle_sidebar(self) -> None:
        if not self._sidebar_widget:
            return
        target_width = 60 if not self._sidebar_collapsed else 210
        self._sidebar_anim = QPropertyAnimation(self._sidebar_widget, b"maximumWidth")
        self._sidebar_anim.setDuration(250)
        self._sidebar_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._sidebar_anim.setStartValue(self._sidebar_widget.width())
        self._sidebar_anim.setEndValue(target_width)
        self._sidebar_anim.finished.connect(lambda: self._on_sidebar_animated(target_width))
        self._sidebar_anim.start()
        self._sidebar_collapsed = not self._sidebar_collapsed

    def _on_sidebar_animated(self, target_width: int) -> None:
        if not self._sidebar_widget:
            return
        self._sidebar_widget.setMinimumWidth(target_width)
        self._sidebar_widget.setMaximumWidth(target_width)
        self._sidebar_widget.setFixedWidth(target_width)
        collapsed = target_width == 60
        for name, widget in self._nav_buttons.items():
            if name.endswith("_text"):
                widget.setVisible(not collapsed)
        if self._lock_btn_text is not None:
            self._lock_btn_text.setVisible(not collapsed)
        if self._sidebar_version_label is not None:
            self._sidebar_version_label.setVisible(not collapsed)

    def _on_nav_clicked(self, name: str) -> None:
        page_map = getattr(self, "_page_map", {})
        self._navigate_to(name, page_map.get(name, 0))

    def _connect_navigation(self) -> None:
        pass

    def _navigate_to(self, name: str, page_index: int) -> None:
        hover_bg = "#C19E56"
        hover_text = "white"
        active_bg = "#7B98AD"
        active_text = "white"
        default_text = "white"

        if self._current_nav and self._current_nav in self._nav_buttons:
            old_btn = self._nav_buttons[self._current_nav]
            if hasattr(old_btn, "setStyleSheet"):
                old_btn.setStyleSheet(
                    f"QWidget {{ border-radius: 6px; background: transparent; }}"
                    f"QWidget:hover {{ background: {hover_bg}; }} QWidget:hover QLabel {{ color: {hover_text}; }}"
                )
            old_text = self._nav_buttons.get(self._current_nav + "_text")
            if old_text and hasattr(old_text, "setStyleSheet"):
                old_text.setStyleSheet(f"color: {default_text}; font-size: 13px; background: transparent;")

        self._current_nav = name
        if name in self._nav_buttons:
            new_btn = self._nav_buttons[name]
            if hasattr(new_btn, "setStyleSheet"):
                new_btn.setStyleSheet(
                    f"QWidget {{ border-radius: 6px; background: {active_bg}; }}"
                )
            new_text = self._nav_buttons.get(name + "_text")
            if new_text and hasattr(new_text, "setStyleSheet"):
                new_text.setStyleSheet(f"color: {active_text}; font-size: 13px; font-weight: bold; background: transparent;")
        self._stack.setCurrentIndex(page_index)
        self._refresh_current_view(name)

    def _on_lock_vault(self) -> None:
        """Lock the vault and close the main window."""
        from app.authentication.vault_lock import lock_vault_and_session
        lock_vault_and_session(self._session_mgr)
        self.vault_locked.emit()
        self.close()

    def _refresh_current_view(self, name: str) -> None:
        if name == "dashboard":
            self._dashboard_vm.load_stats(self._vault_id)
            self._dashboard_vm.load_recent_activity(self._vault_id)
        elif name == "passwords":
            self._password_vm.load_passwords()
        elif name == "notes":
            self._notes_vm.load_notes()
        elif name == "files":
            self._files_vm.load_files()
        elif name == "identity":
            self._identity_vm.load_all()
        elif name == "audit":
            self._audit_vm.load_entries()
        elif name == "backups":
            self._backup_vm.load_backups()

    # ── Service / ViewModel wiring ──

    def _init_services_and_viewmodels(self) -> None:
        from app.core.config import AppConfig
        from app.database.session_factory import create_session
        from app.repositories.api_key_repository import APIKeyRepository
        from app.repositories.audit_repository import AuditRepository
        from app.repositories.file_repository import FileRepository
        from app.repositories.note_repository import NoteRepository
        from app.repositories.password_repository import PasswordRepository
        from app.repositories.software_licence_repository import SoftwareLicenceRepository
        from app.repositories.ssh_key_repository import SSHKeyRepository
        from app.services.audit_service import AuditService
        from app.services.backup_service import BackupService
        from app.services.file_service import FileService
        from app.services.import_export_service import ImportExportService
        from app.services.note_service import NoteService
        from app.services.password_service import PasswordService
        from app.services.report_service import ReportService
        from app.services.search_service import SearchService
        from app.services.security_analysis import SecurityAnalysisService
        from app.ui.viewmodels.audit_viewmodel import AuditViewModel
        from app.ui.viewmodels.backup_viewmodel import BackupViewModel
        from app.ui.viewmodels.dashboard_viewmodel import DashboardViewModel
        from app.ui.viewmodels.digital_identity_viewmodel import DigitalIdentityViewModel
        from app.ui.viewmodels.files_viewmodel import FilesViewModel
        from app.ui.viewmodels.notes_viewmodel import NotesViewModel
        from app.ui.viewmodels.password_viewmodel import PasswordViewModel
        from app.ui.viewmodels.report_viewmodel import ReportViewModel
        from app.ui.viewmodels.search_viewmodel import SearchViewModel
        from app.ui.viewmodels.security_viewmodel import SecurityViewModel
        from app.ui.viewmodels.settings_viewmodel import SettingsViewModel

        config = AppConfig()
        self._session = create_session()

        from app.core.app_container import get_container
        from app.core.session import SessionManager
        self._session_mgr = get_container().resolve(SessionManager)
        self._setup_enhanced_status_bar()

        session = self._session

        pw_repo = PasswordRepository(session)
        note_repo = NoteRepository(session)
        file_repo = FileRepository(session)
        audit_repo = AuditRepository(session)
        ssh_key_repo = SSHKeyRepository(session)
        api_key_repo = APIKeyRepository(session)
        licence_repo = SoftwareLicenceRepository(session)

        self._pw_service = PasswordService(self._vault_key, pw_repo, session)
        self._note_service = NoteService(self._vault_key, note_repo)
        self._file_service = FileService(self._vault_key, file_repo)
        self._audit_service = AuditService(audit_repo)
        self._analysis_service = SecurityAnalysisService(
            self._vault_key, pw_repo, self._pw_service
        )
        self._backup_service = BackupService(
            self._vault_key,
            self._vault_id,
            str(config.database_path),
            str(config.backups_dir),
        )
        self._search_service = SearchService(self._vault_key, pw_repo, note_repo, file_repo)
        self._import_export_service = ImportExportService(self._vault_key, self._pw_service, self._note_service)
        self._report_service = ReportService()

        self._dashboard_vm = DashboardViewModel(pw_repo, note_repo, file_repo, self._analysis_service)
        self._dashboard_vm.set_audit_service(self._audit_service)
        self._password_vm = PasswordViewModel(self._pw_service)
        self._dashboard_vm.set_password_service(self._password_vm._service)
        self._notes_vm = NotesViewModel(self._note_service)
        self._files_vm = FilesViewModel(self._file_service)
        self._security_vm = SecurityViewModel(self._analysis_service)
        self._audit_vm = AuditViewModel(self._audit_service)
        self._backup_vm = BackupViewModel(self._backup_service)
        self._settings_vm = SettingsViewModel()
        self._identity_vm = DigitalIdentityViewModel(
            ssh_key_repo, api_key_repo, licence_repo, self._vault_key
        )
        self._search_vm = SearchViewModel(self._search_service)
        self._report_vm = ReportViewModel(
            self._report_service,
            self._pw_service,
            self._audit_service,
            self._analysis_service,
            ssh_key_repo=ssh_key_repo,
            api_key_repo=api_key_repo,
            licence_repo=licence_repo,
            vault_key=self._vault_key,
        )

        self._dashboard_vm.stats_loaded.connect(self._dashboard_view.update_stats)
        self._dashboard_vm.activity_loaded.connect(self._dashboard_view.update_activity)
        self._password_vm.passwords_loaded.connect(self._password_view.update_passwords)
        self._password_vm.password_selected.connect(self._on_password_selected)
        self._notes_vm.notes_loaded.connect(self._notes_view.update_notes)
        self._files_vm.files_loaded.connect(self._files_view.update_files)
        self._security_vm.analysis_complete.connect(self._security_view.update_analysis)
        self._audit_vm.entries_loaded.connect(self._audit_view.update_audit_log)
        self._backup_vm.backups_loaded.connect(self._backup_view.update_backups)
        self._identity_vm.ssh_keys_loaded.connect(self._identity_view.update_ssh_keys)
        self._identity_vm.api_keys_loaded.connect(self._identity_view.update_api_keys)
        self._identity_vm.licences_loaded.connect(self._identity_view.update_licences)
        self._identity_vm.ssh_key_detail_loaded.connect(self._identity_view.show_ssh_detail)
        self._identity_vm.api_key_detail_loaded.connect(self._identity_view.show_api_detail)
        self._identity_vm.licence_detail_loaded.connect(self._identity_view.show_licence_detail)
        self._identity_view.ssh_key_selected.connect(self._identity_vm.get_ssh_key)
        self._identity_view.api_key_selected.connect(self._identity_vm.get_api_key)
        self._identity_view.licence_selected.connect(self._identity_vm.get_licence)
        self._identity_view.copy_ssh_field.connect(self._on_copy_ssh_field)
        self._identity_view.copy_api_field.connect(self._on_copy_api_field)
        self._identity_view.copy_licence_field.connect(self._on_copy_licence_field)
        self._identity_view.edit_ssh_key.connect(self._on_edit_ssh_key)
        self._identity_view.edit_api_key.connect(self._on_edit_api_key)
        self._identity_view.edit_licence.connect(self._on_edit_licence)
        self._search_vm.results_loaded.connect(self._on_search_results)

        self._report_view._generate_btn.clicked.connect(self._on_generate_report)
        self._report_vm.report_generated.connect(self._on_report_generated)
        self._report_vm.error_occurred.connect(self._on_report_error)

        self._security_view.analyse_requested.connect(self._security_vm.run_analysis)
        self._security_vm.analysis_started.connect(self._security_view.show_scanning)
        self._password_view.password_selected.connect(self._password_vm.select_password)
        self._password_view.add_requested.connect(self._on_add_password)
        self._password_view.generate_requested.connect(self._on_generate_password)
        self._password_view.export_requested.connect(self._on_export_passwords)
        self._password_view.export_json_requested.connect(self._on_export_passwords_json)
        self._password_view.import_requested.connect(self._on_import_passwords)
        self._password_view.delete_requested.connect(self._on_delete_password)
        self._password_view.edit_requested.connect(self._on_edit_password)
        self._password_view.toggle_favourite.connect(self._on_toggle_favourite)
        self._password_view.copy_requested.connect(self._on_copy_password)
        self._password_vm.categories_loaded.connect(self._password_view.set_categories)
        self._password_vm.password_history_loaded.connect(self._password_view.show_password_history)
        self._password_view.manage_categories_requested.connect(self._on_manage_categories)
        self._backup_view.backup_requested.connect(self._backup_vm.create_backup)
        self._backup_view.restore_requested.connect(self._on_restore_backup)
        self._backup_view.delete_backup_requested.connect(self._on_delete_backup)
        self._settings_view.setting_changed.connect(self._on_setting_changed)
        self._settings_view.delete_vault_requested.connect(self._on_delete_vault)
        self._settings_view.check_updates_requested.connect(self._on_check_updates)

        self._notes_view.add_note_requested.connect(self._on_add_note)
        self._notes_view.save_note_requested.connect(self._on_save_note)
        self._notes_view.delete_note_requested.connect(self._on_delete_note)
        self._files_view.encrypt_requested.connect(self._on_encrypt_file)
        self._files_view.encrypt_folder_requested.connect(self._on_encrypt_folder)
        self._files_view.decrypt_requested.connect(self._on_decrypt_file)
        self._files_view.delete_requested.connect(self._on_delete_file)
        self._files_view.clear_all_requested.connect(self._on_clear_all_files)
        self._files_view.decrypt_all_requested.connect(self._on_decrypt_all_files)

        self._notes_vm.error_occurred.connect(
            lambda msg: self.statusBar().showMessage(f"Notes: {msg}")
        )
        self._files_vm.error_occurred.connect(
            lambda msg: self.statusBar().showMessage(f"Files: {msg}")
        )
        self._backup_vm.error_occurred.connect(
            lambda msg: self.statusBar().showMessage(f"Backup: {msg}")
        )
        self._security_vm.analysis_started.connect(
            lambda: self.statusBar().showMessage("Running security scan...")
        )
        self._security_vm.error_occurred.connect(
            lambda msg: self.statusBar().showMessage(f"Security: {msg}")
        )

        self._identity_view.add_ssh_key.connect(self._on_add_ssh_key)
        self._identity_view.add_api_key.connect(self._on_add_api_key)
        self._identity_view.add_licence.connect(self._on_add_licence)
        self._identity_view.delete_ssh_key.connect(self._identity_vm.delete_ssh_key)
        self._identity_view.delete_api_key.connect(self._identity_vm.delete_api_key)
        self._identity_view.delete_licence.connect(self._identity_vm.delete_licence)

        self._dashboard_vm.load_stats(self._vault_id)
        self._dashboard_vm.load_recent_activity(self._vault_id)
        self._password_vm.set_vault(self._vault_id)
        self._notes_vm.set_vault(self._vault_id)
        self._files_vm.set_vault(self._vault_id)
        self._audit_vm.set_vault(self._vault_id)
        self._backup_vm.set_vault(self._vault_id)
        self._identity_vm.set_vault(self._vault_id)
        self._search_vm.set_vault(self._vault_id)
        self._report_vm.set_vault(self._vault_id)
        self._security_vm.set_vault(self._vault_id)
        self._settings_view.load_from_config(config)

        from app.core.app_container import get_container
        from app.core.updates.updater import UpdateService
        from app.workers.update_worker import UpdateWorker

        self._update_service = get_container().resolve(UpdateService)
        self._update_worker: UpdateWorker | None = None

        from app.workers.scheduled_backup_worker import ScheduledBackupWorker

        self._scheduled_backup_worker = ScheduledBackupWorker(self._backup_service, self)
        self._scheduled_backup_worker.backup_created.connect(
            lambda result: self.statusBar().showMessage(
                f"Auto-backup created: {result.get('filename', '')}"
            )
        )
        self._scheduled_backup_worker.backup_error.connect(
            lambda msg: self.statusBar().showMessage(f"Auto-backup failed: {msg}")
        )
        self._scheduled_backup_worker.start()

        self._connect_notifications()

        if self._lock_btn is not None:
            try:
                self._lock_btn.mousePressEvent = lambda event: self._on_lock_vault()
            except Exception:
                pass

    def _connect_notifications(self) -> None:
        """Wire service signals to the notification center."""
        self._backup_vm.error_occurred.connect(
            lambda msg: self._notification_center.add_notification(
                f"Backup failed: {msg}", NotificationSeverity.ERROR
            )
        )
        self._security_vm.analysis_complete.connect(
            lambda result: self._notification_center.add_notification(
                "Security scan complete",
                NotificationSeverity.INFO,
            )
        )
        self._security_vm.error_occurred.connect(
            lambda msg: self._notification_center.add_notification(
                f"Security scan failed: {msg}", NotificationSeverity.ERROR
            )
        )
        self._scheduled_backup_worker.backup_created.connect(
            lambda result: self._notification_center.add_notification(
                f"Auto-backup created: {result.get('filename', '')}",
                NotificationSeverity.INFO,
            )
        )
        self._scheduled_backup_worker.backup_error.connect(
            lambda msg: self._notification_center.add_notification(
                f"Auto-backup failed: {msg}", NotificationSeverity.WARNING,
            )
        )
        self._notes_vm.error_occurred.connect(
            lambda msg: self._notification_center.add_notification(
                f"Notes: {msg}", NotificationSeverity.WARNING,
            )
        )
        self._files_vm.error_occurred.connect(
            lambda msg: self._notification_center.add_notification(
                f"Files: {msg}", NotificationSeverity.WARNING,
            )
        )
        self._report_vm.error_occurred.connect(
            lambda msg: self._notification_center.add_notification(
                f"Report: {msg}", NotificationSeverity.WARNING,
            )
        )

    def _on_password_selected(self, entry: dict) -> None:
        try:
            self._password_view.show_password_detail(entry)
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self, "Cannot Decrypt Entry",
                f"Could not decrypt this password entry: {e}\n\n"
                "The vault may have been locked. Please unlock and try again.",
            )

    def _on_add_password(self) -> None:
        from app.ui.dialogs.password_dialog import PasswordDialog

        categories = self._pw_service.get_categories(self._vault_id)
        dialog = PasswordDialog(edit_mode=False, categories=categories, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            self._password_vm.create_password(
                data["title"], data["username"], data["password"],
                data.get("url", ""), data.get("notes", ""), data.get("expires_at"),
                data.get("category_id", ""),
            )
            self._audit_service.log(self._vault_id, "password_created", "password", data["title"])
            self._dashboard_vm.load_stats(self._vault_id)

    def _on_delete_password(self, entry_id: str) -> None:
        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self, "Delete Password",
            "Are you sure you want to delete this password entry?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._password_vm.delete_password(entry_id)
            self._audit_service.log(self._vault_id, "password_deleted", "password", entry_id)
            self._dashboard_vm.load_stats(self._vault_id)

    def _on_edit_password(self, entry_id: str, current: dict) -> None:
        from app.ui.dialogs.password_dialog import PasswordDialog

        categories = self._pw_service.get_categories(self._vault_id)
        dialog = PasswordDialog(edit_mode=True, current=current, categories=categories, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            updates: dict = {"title": data["title"], "username": data["username"], "url": data["url"], "category_id": data.get("category_id", "")}
            if "password" in data:
                updates["password"] = data["password"]
            if "expires_at" in data:
                updates["expires_at"] = data["expires_at"]
            self._password_vm.update_password(entry_id, **updates)
            self._audit_service.log(self._vault_id, "password_updated", "password", data["title"])

    def _on_toggle_favourite(self, entry_id: str, is_favourite: bool) -> None:
        self._password_vm.toggle_favourite(entry_id, is_favourite)

    def _on_copy_password(self, entry_id: str, field: str) -> None:
        from app.security.clipboard_manager import ClipboardManager

        entry = self._password_vm._service.get_password(entry_id)
        if not entry:
            return
        value = entry.get(field, "")
        if value:
            ClipboardManager().copy_secret(value)
            self.statusBar().showMessage(f"{field.capitalize()} copied to clipboard (clears in 30s)")

    def _on_manage_categories(self) -> None:
        from app.ui.dialogs.category_manager_dialog import CategoryManagerDialog

        cats = self._password_vm._service.get_categories(self._vault_id)
        dialog = CategoryManagerDialog(cats, self)

        dialog.add_requested.connect(self._password_vm.create_category)
        dialog.rename_requested.connect(self._password_vm.update_category)
        dialog.delete_requested.connect(self._password_vm.delete_category)
        self._password_vm.categories_loaded.connect(dialog.update_categories)

        dialog.exec()

    def _on_generate_password(self) -> None:
        from app.ui.dialogs.password_generator_dialog import PasswordGeneratorDialog

        dialog = PasswordGeneratorDialog(self)
        if dialog.exec():
            generated = dialog.get_password()
            if generated:
                from PySide6.QtWidgets import QInputDialog

                title, ok = QInputDialog.getText(self, "Save Generated Password", "Title:")
                if not ok or not title:
                    return
                username, ok = QInputDialog.getText(self, "Save Generated Password", "Username:")
                if not ok:
                    return
                self._password_vm.create_password(title, username, generated)
                self._audit_service.log(self._vault_id, "password_created", "password", title)
                self._dashboard_vm.load_stats(self._vault_id)

    def _on_setting_changed(self, key: str, value) -> None:
        from app.core.config import AppConfig

        config = AppConfig()
        config.set(key, value)
        if key == "appearance.theme":
            self._theme = value
            self._setup_stylesheet(value)
            from app.ui.themes.theme_manager import ThemeManager

            ThemeManager().apply_theme(value)
            for i in range(self._stack.count()):
                w = self._stack.widget(i)
                if hasattr(w, "refresh_theme"):
                    w.refresh_theme()
            self._refresh_sidebar_theme()
        self.statusBar().showMessage(f"Setting saved: {key}")

    def _on_check_updates(self) -> None:
        if self._update_worker is not None:
            return
        from app.workers.update_worker import UpdateWorker

        endpoint = self._settings_view._widgets.get("updates.endpoint")
        endpoint_url = (endpoint.text() or "").strip() if endpoint else ""
        if not endpoint_url:
            endpoint_url = self._update_service.endpoint
        self._update_worker = UpdateWorker(
            self._update_service, action="check", endpoint=endpoint_url
        )
        self._update_worker.signals.update_available.connect(
            self._on_update_available
        )
        self._update_worker.signals.update_not_available.connect(
            self._on_update_not_available
        )
        self._update_worker.signals.error.connect(self._on_update_error)
        self._update_worker.signals.finished.connect(self._on_update_finished)
        from app.core.app_container import get_container

        get_container()  # ensure container initialised
        from PySide6.QtCore import QThreadPool

        QThreadPool.globalInstance().start(self._update_worker)
        self.statusBar().showMessage("Checking for updates...")

    def _on_update_available(self, manifest) -> None:
        from PySide6.QtWidgets import QMessageBox

        msg = (
            f"Version {manifest.version_str} is available (running "
            f"{self._update_service.current_version}).\n\n"
        )
        if manifest.notes:
            msg += f"{manifest.notes}\n\n"
        msg += "Download and install this update?"
        reply = QMessageBox.question(
            self, "Update Available", msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._download_update(manifest)

    def _on_update_not_available(self) -> None:
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(
            self, "Up to Date",
            f"You are running the latest version ({self._update_service.current_version}).",
        )

    def _on_update_error(self, error: str) -> None:
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.warning(
            self, "Update Check Failed",
            f"Could not check for updates: {error}",
        )

    def _on_update_finished(self) -> None:
        self._update_worker = None
        self.statusBar().clearMessage()

    def _download_update(self, manifest) -> None:
        from app.workers.update_worker import UpdateWorker

        self._update_worker = UpdateWorker(
            self._update_service,
            action="download",
            download_url=manifest.url,
            expected_sha256=manifest.sha256,
        )
        self._update_worker.signals.download_progress.connect(
            self._on_download_progress
        )
        self._update_worker.signals.download_complete.connect(
            self._on_download_complete
        )
        self._update_worker.signals.error.connect(self._on_update_error)
        self._update_worker.signals.finished.connect(self._on_update_finished)
        from PySide6.QtCore import QThreadPool

        QThreadPool.globalInstance().start(self._update_worker)
        self.statusBar().showMessage("Downloading update...")

    def _on_download_progress(self, percent: int) -> None:
        self.statusBar().showMessage(f"Downloading update: {percent}%")

    def _on_download_complete(self, zip_path: str) -> None:
        from PySide6.QtWidgets import QMessageBox

        expected = getattr(self._update_worker, "_expected_sha256", None)
        try:
            batch_path = self._update_service.prepare_install(
                zip_path, expected_sha256=expected
            )
        except Exception as exc:  # noqa: BLE001
            self._on_update_error(str(exc))
            return

        reply = QMessageBox.question(
            self, "Install Update",
            "The update has been downloaded and verified. The application will "
            "now close to install it. Click OK to proceed.",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Ok:
            import subprocess

            subprocess.Popen(
                ["cmd", "/c", batch_path],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                close_fds=True,
            )
            from PySide6.QtWidgets import QApplication

            QApplication.instance().quit()

    def _refresh_sidebar_theme(self) -> None:
        is_dark = self._theme == "dark"
        hover_bg = "#2a2a4a" if is_dark else "#d0d0d8"
        hover_text = "#e0e0e0" if is_dark else "#1a1a2e"
        active_bg = "#2a2a4a" if is_dark else "#d0d0d8"

        for name, btn in self._nav_buttons.items():
            if name == self._current_nav:
                btn.setStyleSheet(
                    f"QLabel {{ border-radius: 6px; padding: 6px 12px; font-size: 13px; background: {active_bg}; color: #64B4FF; }}"
                )
            else:
                btn.setStyleSheet(
                    f"QLabel {{ border-radius: 6px; padding: 6px 12px; font-size: 13px; }}"
                    f"QLabel:hover {{ background: {hover_bg}; color: {hover_text}; }}"
                )

    def _on_search_text_changed(self, text: str) -> None:
        if not text.strip():
            self._search_results_container.setVisible(False)
            return
        self._search_vm.search(text)

    def _on_search_results(self, results: list[dict]) -> None:
        layout = self._search_results_layout
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not results:
            lbl = QLabel("No results")
            lbl.setStyleSheet("color: #888; padding: 8px 16px; font-size: 12px;")
            layout.addWidget(lbl)
            self._search_results_container.setVisible(True)
            return

        type_icons = {"password": "🔑", "note": "📝", "file": "📁"}
        for result in results[:10]:
            rtype = result.get("type", "")
            title = result.get("title", "")
            subtitle = result.get("subtitle", "")
            icon = type_icons.get(rtype, "•")

            is_dark = self._theme == "dark"
            search_hover = "#2a2a4a" if is_dark else "#d0d0d8"
            btn = QLabel(f"  {icon}  {title}  —  {subtitle}  [{rtype}]")
            btn.setStyleSheet(
                f"QLabel {{ padding: 8px 16px; font-size: 12px; border-radius: 4px; }}"
                f"QLabel:hover {{ background: {search_hover}; }}"
            )
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.mousePressEvent = lambda _, r=result: self._on_search_result_clicked(r)
            layout.addWidget(btn)

        if len(results) > 10:
            more = QLabel(f"  ... and {len(results) - 10} more results")
            more.setStyleSheet("color: #888; padding: 8px 16px; font-size: 11px;")
            layout.addWidget(more)

        self._search_results_container.setVisible(True)

    def _on_search_result_clicked(self, result: dict) -> None:
        self._search_results_container.setVisible(False)
        self._search_bar.clear()
        rtype = result.get("type", "")
        if rtype == "password":
            self._navigate_to("passwords", 1)
            self._password_vm.select_password(result.get("id", ""))
        elif rtype == "note":
            self._navigate_to("notes", 2)
        elif rtype == "file":
            self._navigate_to("files", 3)

    def _on_export_passwords(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Passwords", "passwords_export.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        try:
            count = self._import_export_service.export_passwords_csv(self._vault_id, path)
            self._audit_service.log(self._vault_id, "passwords_exported", "password", f"{count} entries")
            self.statusBar().showMessage(f"Exported {count} passwords to {path}")
        except Exception as e:
            self.statusBar().showMessage(f"Export failed: {e}")

    def _on_export_passwords_json(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Passwords (JSON)", "passwords_export.json", "JSON Files (*.json)"
        )
        if not path:
            return
        try:
            count = self._import_export_service.export_passwords_json(self._vault_id, path)
            self._audit_service.log(self._vault_id, "passwords_exported_json", "password", f"{count} entries")
            self.statusBar().showMessage(f"Exported {count} passwords to {path}")
        except Exception as e:
            self.statusBar().showMessage(f"JSON export failed: {e}")

    def _on_import_passwords(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getOpenFileName(
            self, "Import Passwords", "", "CSV Files (*.csv)"
        )
        if not path:
            return
        try:
            count = self._import_export_service.import_passwords_csv(self._vault_id, path)
            self._audit_service.log(self._vault_id, "passwords_imported", "password", f"{count} entries")
            self._password_vm.load_passwords()
            self._dashboard_vm.load_stats(self._vault_id)
            self.statusBar().showMessage(f"Imported {count} passwords from {path}")
        except Exception as e:
            self.statusBar().showMessage(f"Import failed: {e}")

    def _on_add_ssh_key(self) -> None:
        from PySide6.QtWidgets import QInputDialog, QLineEdit

        name, ok = QInputDialog.getText(self, "Add SSH Key", "Key Name:")
        if not ok or not name:
            return
        key_type, ok = QInputDialog.getItem(self, "Add SSH Key", "Key Type:", ["ed25519", "rsa", "ecdsa"], 0, False)
        if not ok:
            return
        fingerprint, ok = QInputDialog.getText(self, "Add SSH Key", "Fingerprint:")
        if not ok:
            return
        public_key, ok = QInputDialog.getText(self, "Add SSH Key", "Public Key:")
        if not ok:
            return
        private_key, ok = QInputDialog.getText(self, "Add SSH Key", "Private Key:", QLineEdit.EchoMode.Password)
        if not ok:
            return
        self._identity_vm.add_ssh_key(name, key_type, fingerprint, public_key, private_key)
        self._audit_service.log(self._vault_id, "ssh_key_added", "ssh_key", name)

    def _on_add_api_key(self) -> None:
        from PySide6.QtWidgets import QInputDialog, QLineEdit

        name, ok = QInputDialog.getText(self, "Add API Key", "Key Name:")
        if not ok or not name:
            return
        service, ok = QInputDialog.getText(self, "Add API Key", "Service:")
        if not ok:
            return
        key_value, ok = QInputDialog.getText(self, "Add API Key", "API Key:", QLineEdit.EchoMode.Password)
        if not ok or not key_value:
            return
        self._identity_vm.add_api_key(name, service, key_value)
        self._audit_service.log(self._vault_id, "api_key_added", "api_key", name)

    def _on_add_licence(self) -> None:
        from PySide6.QtWidgets import QInputDialog, QLineEdit

        name, ok = QInputDialog.getText(self, "Add Software Licence", "Software Name:")
        if not ok or not name:
            return
        publisher, ok = QInputDialog.getText(self, "Add Software Licence", "Publisher:")
        if not ok:
            return
        licence_key, ok = QInputDialog.getText(self, "Add Software Licence", "Licence Key:", QLineEdit.EchoMode.Password)
        if not ok or not licence_key:
            return
        self._identity_vm.add_licence(name, publisher, licence_key)
        self._audit_service.log(self._vault_id, "licence_added", "licence", name)

    def _on_copy_ssh_field(self, key_id: str, field: str) -> None:
        entry = self._identity_vm._ssh_repo.get_by_id(key_id)
        if entry is None:
            return
        value = {
            "key_type": entry.key_type,
            "fingerprint": entry.fingerprint,
            "public_key": self._identity_vm._crypto.decrypt_field(self._vault_key, entry.public_key_enc),
            "private_key": self._identity_vm._crypto.decrypt_field(self._vault_key, entry.private_key_enc),
        }.get(field, "")
        if value:
            from PySide6.QtWidgets import QApplication

            QApplication.clipboard().setText(value)
            self.statusBar().showMessage(f"SSH {field} copied to clipboard")

    def _on_copy_api_field(self, key_id: str, field: str) -> None:
        entry = self._identity_vm._api_repo.get_by_id(key_id)
        if entry is None:
            return
        value = {
            "service": entry.service_enc and self._identity_vm._crypto.decrypt_field(self._vault_key, entry.service_enc),
            "key_value": self._identity_vm._crypto.decrypt_field(self._vault_key, entry.key_value_enc),
        }.get(field, "")
        if value:
            from PySide6.QtWidgets import QApplication

            QApplication.clipboard().setText(value)
            self.statusBar().showMessage(f"API {field} copied to clipboard")

    def _on_copy_licence_field(self, key_id: str, field: str) -> None:
        entry = self._identity_vm._licence_repo.get_by_id(key_id)
        if entry is None:
            return
        value = {
            "publisher": entry.publisher_enc and self._identity_vm._crypto.decrypt_field(self._vault_key, entry.publisher_enc),
            "licence_key": self._identity_vm._crypto.decrypt_field(self._vault_key, entry.licence_key_enc),
        }.get(field, "")
        if value:
            from PySide6.QtWidgets import QApplication

            QApplication.clipboard().setText(value)
            self.statusBar().showMessage(f"Licence {field} copied to clipboard")

    def _on_edit_ssh_key(self, key_id: str, data: dict) -> None:
        self._edit_ssh_key_dialog(key_id, data)

    def _on_edit_api_key(self, key_id: str, data: dict) -> None:
        self._edit_api_key_dialog(key_id, data)

    def _on_edit_licence(self, key_id: str, data: dict) -> None:
        self._edit_licence_dialog(key_id, data)

    def _edit_ssh_key_dialog(self, key_id: str, data: dict) -> None:
        from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit SSH Key")
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)
        form = QFormLayout()

        name_edit = QLineEdit(data.get("name", ""))
        type_edit = QLineEdit(data.get("key_type", ""))
        fingerprint_edit = QLineEdit(data.get("fingerprint", ""))
        public_edit = QLineEdit(data.get("public_key", ""))
        private_edit = QLineEdit(data.get("private_key", ""))
        private_edit.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Name:", name_edit)
        form.addRow("Key Type:", type_edit)
        form.addRow("Fingerprint:", fingerprint_edit)
        form.addRow("Public Key:", public_edit)
        form.addRow("Private Key:", private_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._identity_vm.add_ssh_key(
                name_edit.text(), type_edit.text(), fingerprint_edit.text(),
                public_edit.text(), private_edit.text(),
            )
            self._identity_vm.delete_ssh_key(key_id)
            self._audit_service.log(self._vault_id, "ssh_key_edited", "ssh_key", name_edit.text())

    def _edit_api_key_dialog(self, key_id: str, data: dict) -> None:
        from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit API Key")
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)
        form = QFormLayout()

        name_edit = QLineEdit(data.get("name", ""))
        service_edit = QLineEdit(data.get("service", ""))
        value_edit = QLineEdit(data.get("key_value", ""))
        value_edit.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Name:", name_edit)
        form.addRow("Service:", service_edit)
        form.addRow("API Key:", value_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._identity_vm.add_api_key(name_edit.text(), service_edit.text(), value_edit.text())
            self._identity_vm.delete_api_key(key_id)
            self._audit_service.log(self._vault_id, "api_key_edited", "api_key", name_edit.text())

    def _edit_licence_dialog(self, key_id: str, data: dict) -> None:
        from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Software Licence")
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)
        form = QFormLayout()

        name_edit = QLineEdit(data.get("name", ""))
        publisher_edit = QLineEdit(data.get("publisher", ""))
        key_edit = QLineEdit(data.get("licence_key", ""))
        key_edit.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Name:", name_edit)
        form.addRow("Publisher:", publisher_edit)
        form.addRow("Licence Key:", key_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._identity_vm.add_licence(name_edit.text(), publisher_edit.text(), key_edit.text())
            self._identity_vm.delete_licence(key_id)
            self._audit_service.log(self._vault_id, "licence_edited", "licence", name_edit.text())

    def _on_add_note(self) -> None:
        from PySide6.QtWidgets import QInputDialog

        title, ok = QInputDialog.getText(self, "New Note", "Note Title:")
        if not ok or not title:
            return
        self._notes_vm.create_note(title, "")
        self._audit_service.log(self._vault_id, "note_created", "note", title)

    def _on_save_note(self, note_id: str, content: str) -> None:
        self._notes_vm.update_note(note_id, content)
        self._audit_service.log(self._vault_id, "note_updated", "note", note_id)

    def _on_delete_note(self, note_id: str) -> None:
        self._notes_vm.delete_note(note_id)
        self._audit_service.log(self._vault_id, "note_deleted", "note", note_id)
        self.statusBar().showMessage("Note deleted")

    def _on_encrypt_file(self, delete_original: bool = False) -> None:
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Encrypt")
        if not file_path:
            return
        from app.core.config import AppConfig

        config = AppConfig()
        output_dir = str(config.backups_dir / "encrypted_files" / self._vault_id)
        self._files_vm.encrypt_file(file_path, output_dir, delete_original)
        self._audit_service.log(self._vault_id, "file_encrypted", "file", file_path)
        self.statusBar().showMessage(f"File encrypted: {file_path}")

    def _on_encrypt_folder(self, delete_original: bool = False) -> None:
        from PySide6.QtWidgets import QFileDialog

        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Encrypt")
        if not folder_path:
            return
        from app.core.config import AppConfig

        config = AppConfig()
        output_dir = str(config.backups_dir / "encrypted_files" / self._vault_id)
        self._files_vm.encrypt_folder(folder_path, output_dir, delete_original)
        self._audit_service.log(self._vault_id, "folder_encrypted", "file", folder_path)
        self.statusBar().showMessage(f"Folder encryption started: {folder_path}")

    def _on_decrypt_file(self, file_id: str) -> None:
        from PySide6.QtWidgets import QFileDialog

        original_name = self._file_service.get_file_original_name(file_id)
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save Decrypted File", original_name
        )
        if not output_path:
            return
        self._files_vm.decrypt_file(file_id, output_path)
        self._audit_service.log(self._vault_id, "file_decrypted", "file", output_path)
        self.statusBar().showMessage(f"File decrypted to: {output_path}")

    def _on_delete_file(self, file_id: str) -> None:
        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self, "Delete File",
            "Are you sure you want to permanently delete this encrypted file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._files_vm.delete_file(file_id)
            self._audit_service.log(self._vault_id, "file_deleted", "file", file_id)
            self.statusBar().showMessage("File deleted")

    def _on_clear_all_files(self) -> None:
        self._files_view.clear_files()
        self._files_view._flash_status("Deleting all encrypted files...", "#EF4444")
        self._files_vm.delete_all_files()
        self._audit_service.log(self._vault_id, "all_files_deleted", "file", "all")
        self._files_view._flash_status("All encrypted files deleted.", "#EF4444")

    def _on_decrypt_all_files(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        output_dir = QFileDialog.getExistingDirectory(self, "Select Folder for Decrypted Files")
        if not output_dir:
            return
        self._files_view._flash_status("Decrypting all files...", "#3B82F6")
        self._files_vm.decrypt_all_files(output_dir)
        self._audit_service.log(self._vault_id, "all_files_decrypted", "file", output_dir)
        self._files_view._flash_status(f"All files decrypted to: {output_dir}", "#10B981")

    def _on_restore_backup(self, backup_path: str) -> None:
        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self, "Restore Backup",
            "This will replace the current vault data with the backup.\n"
            "The application will return to the unlock screen. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from app.core.app_container import get_container
                from app.core.config import AppConfig
                from app.core.session import SessionManager
                from app.database.session_factory import dispose_engine, init_session_factory

                self._session.close()
                dispose_engine()

                self._backup_vm.restore_backup(backup_path)

                container = get_container()
                config = container.resolve(AppConfig)
                init_session_factory(config)

                session_mgr = container.resolve(SessionManager)
                session_mgr.lock()

                self.vault_locked.emit()
                self.close()
            except Exception as e:
                QMessageBox.critical(self, "Restore Failed", f"Failed to restore backup:\n{e}")

    def _on_delete_backup(self, backup_path: str) -> None:
        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self, "Delete Backup",
            "Are you sure you want to permanently delete this backup?\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self._backup_vm.delete_backup(backup_path)
                self.statusBar().showMessage("Backup deleted")
            except Exception as e:
                QMessageBox.critical(self, "Delete Failed", f"Failed to delete backup:\n{e}")

    def _on_generate_report(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        report_type = self._report_view.get_selected_report_type()
        if report_type is None:
            self.statusBar().showMessage("No report type selected")
            return

        default_name = self._report_view.get_default_filename()
        file_filter = self._report_view.get_file_filter()
        path, _ = QFileDialog.getSaveFileName(self, "Save Report", default_name, file_filter)
        if not path:
            return

        self._report_view.show_generating()
        self._audit_service.log(self._vault_id, "report_generated", "report", report_type)
        self._report_vm.generate_report(report_type, path)

    def _on_report_generated(self, path: str) -> None:
        self._report_view.show_complete()
        self._report_view.set_status(f"Report saved to {path}", success=True)
        self.statusBar().showMessage(f"Report generated: {path}")

    def _on_report_error(self, message: str) -> None:
        self._report_view.show_complete()
        self._report_view.set_status(f"Error: {message}", success=False)
        self.statusBar().showMessage(f"Report failed: {message}")

    def _on_delete_vault(self) -> None:
        from app.ui.dialogs.delete_vault_dialog import DeleteVaultDialog

        dialog = DeleteVaultDialog(self)
        if not dialog.exec():
            return

        from pathlib import Path

        from app.models.vault import Vault
        from app.utils.secure_delete import secure_delete_file

        self._session.expire_all()

        vault = self._session.query(Vault).first()
        if vault is None:
            return

        for pw_entry in vault.passwords:
            self._session.delete(pw_entry)
        for note in vault.notes:
            self._session.delete(note)
        for file_meta in vault.files:
            enc_path = Path(file_meta.encrypted_path)
            if enc_path.exists():
                secure_delete_file(str(enc_path))
            self._session.delete(file_meta)
        for cat in vault.categories:
            self._session.delete(cat)
        for tag in vault.tags:
            self._session.delete(tag)
        for audit in vault.audit_logs:
            self._session.delete(audit)
        for ssh in vault.ssh_keys:
            self._session.delete(ssh)
        for api in vault.api_keys:
            self._session.delete(api)
        for lic in vault.software_licences:
            self._session.delete(lic)
        for backup in vault.backup_history:
            bp = Path(backup.file_path) if backup.file_path else None
            if bp and bp.exists():
                secure_delete_file(str(bp))
            self._session.delete(backup)
        for rk in vault.recovery_keys:
            self._session.delete(rk)
        for se in vault.security_events:
            self._session.delete(se)
        for setting in vault.user_settings:
            self._session.delete(setting)

        self._session.delete(vault)
        self._session.commit()

        from app.core.app_container import get_container
        from app.core.session import SessionManager

        container = get_container()
        session_mgr = container.resolve(SessionManager)
        session_mgr.lock()

        self.vault_deleted.emit()
        self.close()
