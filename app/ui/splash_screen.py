"""Splash screen for SecureVault Pro startup."""

import os

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import QSplashScreen

from app.core.constants import APP_DESCRIPTION, APP_NAME, APP_TAGLINE, APP_VERSION

_WIDTH = 500
_HEIGHT = 340
_BAR_Y = 270
_BAR_H = 6
_BAR_MARGIN = 60
_ICON_SIZE = 48
_ICON_Y = 16


class SplashScreen(QSplashScreen):
    """Animated splash screen displayed during application startup."""

    def __init__(self) -> None:
        self._pixmap = QPixmap(_WIDTH, _HEIGHT)
        self._pixmap.fill(QColor(30, 30, 30))

        self._progress = 0
        self._draw_static_elements()

        super().__init__(self._pixmap)
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)

        self._timer = QTimer(self)
        self._timer.setInterval(20)
        self._timer.timeout.connect(self._tick)

    # ── Public API ──

    def start_progress(self) -> None:
        """Start the progress bar animation."""
        self._timer.start()

    def finish(self) -> None:
        """Close the splash screen."""
        self._timer.stop()
        self.close()

    # ── Drawing ──

    def _load_icon(self) -> QPixmap:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, "resources", "icons", "vault.png")
        if os.path.exists(icon_path):
            return QPixmap(icon_path)
        return QPixmap()

    def _draw_static_elements(self) -> None:
        painter = QPainter(self._pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, 0, _HEIGHT)
        gradient.setColorAt(0, QColor(22, 22, 42))
        gradient.setColorAt(1, QColor(14, 14, 26))
        painter.fillRect(self._pixmap.rect(), gradient)

        icon = self._load_icon()
        if not icon.isNull():
            icon = icon.scaled(
                _ICON_SIZE,
                _ICON_SIZE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            icon_x = (_WIDTH - _ICON_SIZE) // 2
            painter.drawPixmap(icon_x, _ICON_Y, icon)

        painter.setPen(QColor(100, 180, 255))
        painter.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        painter.drawText(
            self._pixmap.rect().adjusted(0, 100, 0, 0),
            Qt.AlignmentFlag.AlignHCenter,
            APP_NAME,
        )

        painter.setPen(QColor(150, 150, 170))
        painter.setFont(QFont("Segoe UI", 11))
        painter.drawText(
            self._pixmap.rect().adjusted(0, 155, 0, 0),
            Qt.AlignmentFlag.AlignHCenter,
            APP_TAGLINE,
        )

        painter.setPen(QColor(120, 120, 140))
        painter.setFont(QFont("Segoe UI", 10))
        painter.drawText(
            self._pixmap.rect().adjusted(0, 180, 0, 0),
            Qt.AlignmentFlag.AlignHCenter,
            APP_DESCRIPTION,
        )

        painter.setPen(QColor(100, 100, 120))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(
            self._pixmap.rect().adjusted(0, 230, 0, 0),
            Qt.AlignmentFlag.AlignHCenter,
            f"v{APP_VERSION}",
        )

        painter.setPen(QColor(80, 80, 100))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(
            self._pixmap.rect().adjusted(0, 310, 0, 0),
            Qt.AlignmentFlag.AlignHCenter,
            "Powered by Devallix",
        )

        painter.end()

    def _draw_progress(self) -> None:
        painter = QPainter(self._pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, 0, _HEIGHT)
        gradient.setColorAt(0, QColor(22, 22, 42))
        gradient.setColorAt(1, QColor(14, 14, 26))
        painter.fillRect(self._pixmap.rect(), gradient)

        icon = self._load_icon()
        if not icon.isNull():
            icon = icon.scaled(
                _ICON_SIZE,
                _ICON_SIZE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            icon_x = (_WIDTH - _ICON_SIZE) // 2
            painter.drawPixmap(icon_x, _ICON_Y, icon)

        painter.setPen(QColor(100, 180, 255))
        painter.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        painter.drawText(
            self._pixmap.rect().adjusted(0, 90, 0, 0),
            Qt.AlignmentFlag.AlignHCenter,
            APP_NAME,
        )

        painter.setPen(QColor(150, 150, 170))
        painter.setFont(QFont("Segoe UI", 11))
        painter.drawText(
            self._pixmap.rect().adjusted(0, 145, 0, 0),
            Qt.AlignmentFlag.AlignHCenter,
            APP_TAGLINE,
        )

        painter.setPen(QColor(120, 120, 140))
        painter.setFont(QFont("Segoe UI", 10))
        painter.drawText(
            self._pixmap.rect().adjusted(0, 170, 0, 0),
            Qt.AlignmentFlag.AlignHCenter,
            APP_DESCRIPTION,
        )

        painter.setPen(QColor(100, 100, 120))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(
            self._pixmap.rect().adjusted(0, 220, 0, 0),
            Qt.AlignmentFlag.AlignHCenter,
            f"v{APP_VERSION}",
        )

        bar_full_w = _WIDTH - 2 * _BAR_MARGIN
        bar_w = int(bar_full_w * self._progress / 100)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(40, 40, 60))
        painter.drawRoundedRect(_BAR_MARGIN, _BAR_Y, bar_full_w, _BAR_H, 3, 3)

        if bar_w > 0:
            bar_gradient = QLinearGradient(_BAR_MARGIN, 0, _BAR_MARGIN + bar_full_w, 0)
            bar_gradient.setColorAt(0, QColor(60, 120, 220))
            bar_gradient.setColorAt(1, QColor(100, 180, 255))
            painter.setBrush(bar_gradient)
            painter.drawRoundedRect(_BAR_MARGIN, _BAR_Y, bar_w, _BAR_H, 3, 3)

        painter.setPen(QColor(80, 80, 100))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(
            self._pixmap.rect().adjusted(0, 310, 0, 0),
            Qt.AlignmentFlag.AlignHCenter,
            "Powered by Devallix",
        )

        painter.end()

        self.setPixmap(self._pixmap)

    def _tick(self) -> None:
        if self._progress < 100:
            self._progress = min(100, self._progress + 2)
            self._draw_progress()
        else:
            self._timer.stop()
