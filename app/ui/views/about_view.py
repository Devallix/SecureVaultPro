"""About page with app and developer information."""

import os

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QFont, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.core.constants import APP_NAME, APP_TAGLINE, APP_VERSION


class AboutView(QWidget):
    """About page showing app details and developer info."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    @staticmethod
    def _theme_colors():
        from app.core.config import AppConfig
        is_dark = AppConfig().get("appearance.theme", "dark") == "dark"
        if is_dark:
            return {
                "accent": "#64B4FF",
                "muted": "#aaa",
                "muted2": "#888",
                "muted3": "#ccc",
                "muted4": "#999",
                "text": "#e0e0e0",
                "card_bg": "#16162a",
                "card_border": "#2a2a4a",
                "sep": "#2a2a4a",
                "dev_card_bg": "#2a2a3a",
            }
        else:
            return {
                "accent": "#3B82F6",
                "muted": "#666",
                "muted2": "#888",
                "muted3": "#555",
                "muted4": "#777",
                "text": "#1a1a2e",
                "card_bg": "#ffffff",
                "card_border": "#d0d0d8",
                "sep": "#d0d0d8",
                "dev_card_bg": "#e8e8ed",
            }

    def refresh_theme(self) -> None:
        C = self._theme_colors()
        self._tagline.setStyleSheet(f"color: {C['muted']};")
        self._version_label.setStyleSheet(f"color: {C['muted2']};")
        self._desc.setStyleSheet(f"color: {C['muted3']}; line-height: 1.5;")
        self._sep.setStyleSheet(f"color: {C['sep']};")
        self._dev_header.setStyleSheet(f"color: {C['text']};")
        self._dev_card.setStyleSheet(
            f"QFrame {{ background: {C['dev_card_bg']}; border: 1px solid {C['card_border']}; border-radius: 10px; }}"
        )
        self._dev_role.setStyleSheet(f"color: {C['muted']}; border: none;")
        self._dev_bio.setStyleSheet(f"color: {C['muted4']}; border: none; line-height: 1.4;")

    def _build_ui(self) -> None:
        C = self._theme_colors()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(20)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)

        vault_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
            "resources", "icons", "vault.png",
        )
        if os.path.exists(vault_path):
            icon_label = QLabel()
            icon_label.setPixmap(QPixmap(vault_path).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            icon_label.setFixedSize(48, 48)
            title_row.addWidget(icon_label)

        title = QLabel(APP_NAME)
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C['accent']};")
        title_row.addWidget(title)
        title_row.addStretch()

        layout.addLayout(title_row)

        self._tagline = QLabel(APP_TAGLINE)
        self._tagline.setFont(QFont("Segoe UI", 12))
        self._tagline.setStyleSheet(f"color: {C['muted']};")
        layout.addWidget(self._tagline)

        layout.addSpacing(10)

        self._version_label = QLabel(f"Version {APP_VERSION}")
        self._version_label.setFont(QFont("Segoe UI", 11))
        self._version_label.setStyleSheet(f"color: {C['muted2']};")
        layout.addWidget(self._version_label)

        layout.addSpacing(16)

        self._desc = QLabel(
            "SecureVault Pro is an enterprise-grade file encryption and password management "
            "desktop application. It provides AES-256-GCM and ChaCha20 encryption, "
            "secure password generation, encrypted notes, digital identity management "
            "(SSH keys, API keys, software licences), security analysis, and encrypted backups."
        )
        self._desc.setWordWrap(True)
        self._desc.setFont(QFont("Segoe UI", 11))
        self._desc.setStyleSheet(f"color: {C['muted3']}; line-height: 1.5;")
        layout.addWidget(self._desc)

        layout.addSpacing(20)

        self._sep = QFrame()
        self._sep.setFrameShape(QFrame.Shape.HLine)
        self._sep.setStyleSheet(f"color: {C['sep']};")
        layout.addWidget(self._sep)

        layout.addSpacing(10)

        devallix_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
            "resources", "images", "devallix.png",
        )

        self._dev_header = QLabel("Developer")
        self._dev_header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self._dev_header.setStyleSheet(f"color: {C['text']};")
        layout.addWidget(self._dev_header)

        layout.addSpacing(8)

        self._dev_card = QFrame()
        self._dev_card.setStyleSheet(
            f"QFrame {{ background: {C['dev_card_bg']}; border: 1px solid {C['card_border']}; border-radius: 10px; }}"
        )
        dev_card_layout = QHBoxLayout(self._dev_card)
        dev_card_layout.setContentsMargins(20, 20, 20, 20)
        dev_card_layout.setSpacing(24)

        if os.path.exists(devallix_path):
            pixmap = QPixmap(devallix_path)
            img_label = QLabel()
            img_label.setPixmap(pixmap.scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            img_label.setFixedSize(160, 160)
            img_label.setStyleSheet("border: none;")
            dev_card_layout.addWidget(img_label)

        dev_info = QVBoxLayout()
        dev_info.setSpacing(6)

        dev_name = QLabel("Devallix")
        dev_name.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        dev_name.setStyleSheet("color: #64B4FF; border: none;")
        dev_info.addWidget(dev_name)

        self._dev_role = QLabel("Software Developer")
        self._dev_role.setFont(QFont("Segoe UI", 11))
        self._dev_role.setStyleSheet(f"color: {C['muted']}; border: none;")
        dev_info.addWidget(self._dev_role)

        dev_info.addSpacing(6)

        self._dev_bio = QLabel(
            "Full-stack developer specializing in security-focused applications, "
            "desktop software, and modern web technologies."
        )
        self._dev_bio.setWordWrap(True)
        self._dev_bio.setFont(QFont("Segoe UI", 10))
        self._dev_bio.setStyleSheet(f"color: {C['muted4']}; border: none; line-height: 1.4;")
        dev_info.addWidget(self._dev_bio)

        dev_info.addSpacing(6)

        dev_url = QLabel("https://www.devallix.com")
        dev_url.setFont(QFont("Segoe UI", 10))
        dev_url.setStyleSheet("color: #64B4FF; text-decoration: underline; border: none;")
        dev_url.setCursor(Qt.CursorShape.PointingHandCursor)
        dev_url.mousePressEvent = lambda e: QDesktopServices.openUrl(QUrl("https://www.devallix.com"))
        dev_info.addWidget(dev_url)

        dev_card_layout.addLayout(dev_info, 1)

        layout.addWidget(self._dev_card)

        layout.addStretch()

        scroll.setWidget(content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
