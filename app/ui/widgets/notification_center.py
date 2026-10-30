"""Notification center widget with bell icon and dropdown popup."""

import time
from dataclasses import dataclass, field
from enum import Enum

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class NotificationSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Notification:
    id: int
    message: str
    severity: NotificationSeverity
    timestamp: float = field(default_factory=time.time)
    dismissed: bool = False


_SEVERITY_COLORS = {
    NotificationSeverity.INFO: "#64B4FF",
    NotificationSeverity.WARNING: "#F59E0B",
    NotificationSeverity.ERROR: "#EF4444",
}

_SEVERITY_ICONS = {
    NotificationSeverity.INFO: "\u2139",
    NotificationSeverity.WARNING: "\u26A0",
    NotificationSeverity.ERROR: "\u2716",
}

_MAX_NOTIFICATIONS = 50


class NotificationCenter(QWidget):
    """Bell-icon button that shows a popup with dismissible notifications."""

    notification_added = Signal(object)
    notification_dismissed = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._notifications: list[Notification] = []
        self._next_id = 1
        self._popup_visible = False
        self._popup: QFrame | None = None
        self._list_layout: QVBoxLayout | None = None
        self._empty_label: QLabel | None = None

        self._build_ui()

    # ── Public API ──

    def add_notification(
        self, message: str, severity: NotificationSeverity = NotificationSeverity.INFO
    ) -> None:
        """Add a new notification and update the badge."""
        notif = Notification(id=self._next_id, message=message, severity=severity)
        self._next_id += 1
        self._notifications.insert(0, notif)

        if len(self._notifications) > _MAX_NOTIFICATIONS:
            self._notifications = self._notifications[:_MAX_NOTIFICATIONS]

        self._refresh_badge()
        self.notification_added.emit(notif)

    def dismiss_notification(self, notif_id: int) -> None:
        """Remove a notification by id."""
        self._notifications = [n for n in self._notifications if n.id != notif_id]
        self._refresh_badge()
        if self._popup_visible:
            self._refresh_popup_list()
        self.notification_dismissed.emit(notif_id)

    def clear_all(self) -> None:
        """Dismiss every notification."""
        self._notifications.clear()
        self._refresh_badge()
        if self._popup_visible:
            self._refresh_popup_list()

    @property
    def count(self) -> int:
        return len(self._notifications)

    # ── UI construction ──

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._bell_btn = QPushButton("\U0001F514")
        self._bell_btn.setFixedSize(40, 40)
        self._bell_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._bell_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; font-family: 'Segoe UI Emoji', 'Segoe UI Symbol'; font-size: 24px; padding: 0px; }"
            "QPushButton:hover { background: #2a2a4a; border-radius: 6px; }"
        )
        self._bell_btn.clicked.connect(self._toggle_popup)
        layout.addWidget(self._bell_btn)

        self._badge_label = QLabel(self)
        self._badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge_label.setFixedSize(18, 18)
        self._badge_label.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self._badge_label.setStyleSheet(
            "background: #EF4444; color: white; border-radius: 9px; font-size: 9px;"
        )
        self._badge_label.setVisible(False)

    def _ensure_popup(self) -> None:
        """Create the popup as a child of the top-level window so it is not clipped."""
        if self._popup is not None:
            return
        win = self.window()
        self._popup = QFrame(win)
        self._popup.setObjectName("notif_popup")
        self._popup.setStyleSheet(
            "QFrame#notif_popup { background: #16162a; border: 1px solid #2a2a4a; "
            "border-radius: 8px; }"
        )
        self._popup.setFixedWidth(360)
        self._popup.setVisible(False)

        popup_layout = QVBoxLayout(self._popup)
        popup_layout.setContentsMargins(0, 0, 0, 0)
        popup_layout.setSpacing(0)

        header = QFrame()
        header.setStyleSheet("background: #16162a; border-bottom: 1px solid #2a2a4a;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)

        title = QLabel("Notifications")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0e0; background: transparent;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        clear_btn = QPushButton("Clear all")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #64B4FF;"
            " border: none; font-size: 11px; }"
            "QPushButton:hover { color: #93C5FF; }"
        )
        clear_btn.clicked.connect(self.clear_all)
        header_layout.addWidget(clear_btn)

        popup_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea { background: #16162a; border: none; }"
            "QScrollArea > QWidget > QWidget { background: #16162a; }"
        )

        list_widget = QWidget()
        self._list_layout = QVBoxLayout(list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)
        self._list_layout.addStretch()
        scroll.setWidget(list_widget)
        popup_layout.addWidget(scroll)

        self._empty_label = QLabel("No notifications")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet(
            "color: #666; padding: 24px; font-size: 12px; background: transparent;"
        )
        popup_layout.addWidget(self._empty_label)

    # ── Badge ──

    def _refresh_badge(self) -> None:
        n = self.count
        if n > 0:
            self._badge_label.setText(str(min(n, 99)))
            self._badge_label.setVisible(True)
            self._badge_label.move(self._bell_btn.width() - 12, -4)
        else:
            self._badge_label.setVisible(False)

    # ── Popup ──

    def _toggle_popup(self) -> None:
        if self._popup_visible:
            self._hide_popup()
        else:
            self._show_popup()

    def _show_popup(self) -> None:
        self._ensure_popup()
        self._refresh_popup_list()
        self._popup.setVisible(True)
        self._popup.raise_()
        ph = self._popup.sizeHint().height()
        self._popup.setFixedHeight(min(max(ph, 120), 400))
        btn_pos = self._bell_btn.mapToGlobal(self._bell_btn.rect().bottomLeft())
        popup_x = btn_pos.x() - self._popup.width() + self._bell_btn.width()
        popup_y = btn_pos.y() + 4
        self._popup.move(popup_x, popup_y)
        self._popup_visible = True
        self.window().installEventFilter(self)

    def _hide_popup(self) -> None:
        if self._popup is not None:
            self._popup.setVisible(False)
        self._popup_visible = False
        self.window().removeEventFilter(self)

    def _refresh_popup_list(self) -> None:
        if self._list_layout is None:
            return
        while self._list_layout.count():
            child = self._list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if self._empty_label is not None:
            self._empty_label.setVisible(len(self._notifications) == 0)

        for notif in self._notifications:
            if notif.dismissed:
                continue
            row = self._create_notification_row(notif)
            self._list_layout.addWidget(row)

        self._list_layout.addStretch()

    def _create_notification_row(self, notif: Notification) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background: transparent; border-bottom: 1px solid #2a2a4a; }"
            "QFrame:hover { background: #1e1e3a; }"
        )
        frame.setFixedHeight(48)

        row_layout = QHBoxLayout(frame)
        row_layout.setContentsMargins(12, 6, 8, 6)
        row_layout.setSpacing(8)

        icon = QLabel(_SEVERITY_ICONS[notif.severity])
        icon.setFixedSize(24, 24)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        color = _SEVERITY_COLORS[notif.severity]
        icon.setStyleSheet(
            f"color: {color}; font-size: 14px; background: transparent;"
        )
        row_layout.addWidget(icon)

        msg = QLabel(notif.message)
        msg.setStyleSheet("color: #ccc; font-size: 11px; background: transparent;")
        msg.setWordWrap(True)
        row_layout.addWidget(msg, 1)

        dismiss_btn = QPushButton("\u2715")
        dismiss_btn.setFixedSize(20, 20)
        dismiss_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        dismiss_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #666; border: none; font-size: 10px; }"
            "QPushButton:hover { color: #EF4444; }"
        )
        dismiss_btn.clicked.connect(lambda _, nid=notif.id: self.dismiss_notification(nid))
        row_layout.addWidget(dismiss_btn)

        return frame

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._badge_label.move(self._bell_btn.width() - 12, -4)

    def eventFilter(self, obj, event) -> None:  # noqa: N802
        if self._popup_visible and obj is self.window():
            if event.type() == event.Type.MouseButtonPress:
                if self._popup is not None and not self._popup.geometry().contains(event.globalPos()):
                    self._hide_popup()
        return super().eventFilter(obj, event)
