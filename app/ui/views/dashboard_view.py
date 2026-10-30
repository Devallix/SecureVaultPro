"""Dashboard view showing vault overview statistics."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

TABLE_BG = "#1D263F"


class DashboardView(QWidget):
    """Dashboard overview with vault statistics and health."""

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
                "text": "#e0e0e0",
                "text_muted": "#94A3B8",
                "card_bg": "#1D263F",
                "card_border": "#2D3A5E",
            }
        else:
            return {
                "accent": "#3B82F6",
                "text": "#1a1a2e",
                "text_muted": "#64748B",
                "card_bg": "#1D263F",
                "card_border": "#2D3A5E",
            }

    def refresh_theme(self) -> None:
        C = self._theme_colors()
        self._title.setStyleSheet(f"color: {C['accent']}; font-size: 24px; font-weight: bold;")
        self._subtitle.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px;")
        if hasattr(self, "_last_stats"):
            self.update_stats(self._last_stats)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        # ── Header ──
        header = QHBoxLayout()
        self._title = QLabel("Dashboard")
        self._title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self._title.setStyleSheet("color: #FFFFFF;")
        header.addWidget(self._title)
        header.addStretch()
        layout.addLayout(header)

        self._subtitle = QLabel("Overview of your vault security at a glance")
        self._subtitle.setStyleSheet("color: #94A3B8; font-size: 13px;")
        layout.addWidget(self._subtitle)

        layout.addSpacing(8)

        # ── Stat cards ──
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        self._passwords_card = self._create_stat_card("Passwords", "0", "#3B82F6", "🔐")
        self._notes_card = self._create_stat_card("Secure Notes", "0", "#10B981", "📝")
        self._files_card = self._create_stat_card("Encrypted Files", "0", "#F59E0B", "📁")
        self._health_card = self._create_stat_card("Health Score", "0", "#8B5CF6", "🛡️")

        cards_layout.addWidget(self._passwords_card)
        cards_layout.addWidget(self._notes_card)
        cards_layout.addWidget(self._files_card)
        cards_layout.addWidget(self._health_card)

        layout.addLayout(cards_layout)
        layout.addSpacing(4)

        # ── Recent Activity ──
        activity_panel = self._create_panel("Recent Activity", "🕒")
        activity_layout = activity_panel.layout()

        self._activity_list = QListWidget()
        self._activity_list.setAlternatingRowColors(True)
        self._activity_list.setStyleSheet(
            f"QListWidget {{ border: none; background: {TABLE_BG}; border-radius: 8px; font-size: 12px; color: #E2E8F0; }} "
            f"QListWidget::item {{ padding: 8px 12px; border-bottom: 1px solid #2D3A5E; }} "
            f"QListWidget::item:selected {{ background: #33415E; color: #64B4FF; }}"
        )
        self._activity_list.addItem(QListWidgetItem("No recent activity to display."))
        activity_layout.addWidget(self._activity_list)

        activity_panel.setMinimumWidth(320)
        layout.addWidget(activity_panel, 0)
        layout.addStretch()

    def _create_stat_card(self, title: str, value: str, color: str, emoji: str) -> QFrame:
        card = QFrame()
        card.setMinimumHeight(110)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setStyleSheet(
            f"""
            QFrame {{
                background: {TABLE_BG};
                border: 1px solid #2D3A5E;
                border-radius: 12px;
            }}
            QFrame:hover {{
                border: 1px solid {color};
            }}
            """
        )

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(14)

        emoji_label = QLabel(emoji)
        emoji_label.setStyleSheet(f"color: {color}; font-size: 24px;")
        emoji_label.setFixedSize(36, 36)
        layout.addWidget(emoji_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        label = QLabel(title)
        label.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 600;")
        text_layout.addWidget(label)

        value_label = QLabel(value)
        value_label.setObjectName("stat_value")
        value_label.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #FFFFFF;")
        text_layout.addWidget(value_label)

        secondary = QLabel("")
        secondary.setObjectName("stat_secondary")
        secondary.setStyleSheet("color: #64748B; font-size: 10px; font-weight: 500;")
        text_layout.addWidget(secondary)

        text_layout.addStretch()
        layout.addLayout(text_layout, 1)
        layout.addStretch(0)

        return card

    def _create_panel(self, title: str, emoji: str) -> QFrame:
        panel = QFrame()
        panel.setStyleSheet(
            f"""
            QFrame {{
                background: {TABLE_BG};
                border: 1px solid #2D3A5E;
                border-radius: 12px;
            }}
            """
        )
        panel.setMinimumWidth(280)
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(10)

        emoji_label = QLabel(emoji)
        emoji_label.setStyleSheet("font-size: 18px;")
        emoji_label.setFixedSize(24, 24)
        header.addWidget(emoji_label)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #FFFFFF;")
        title_label.setMinimumWidth(120)
        header.addWidget(title_label)

        header.addStretch()
        layout.addLayout(header)

        return panel

    def update_stats(self, stats: dict) -> None:
        """Update displayed statistics."""
        self._last_stats = stats
        weak = stats.get("weak_count", 0)
        expired = stats.get("expired_count", 0)
        password_parts = []
        if weak:
            password_parts.append(f"{weak} weak")
        if expired:
            password_parts.append(f"{expired} expired")
        self._set_secondary(self._passwords_card, " · ".join(password_parts) if password_parts else "All strong")

        self._set_secondary(self._notes_card, "")

        file_size = stats.get("total_file_size", 0)
        if file_size >= 1024 * 1024:
            size_str = f"{file_size / (1024 * 1024):.1f} MB stored"
        elif file_size >= 1024:
            size_str = f"{file_size / 1024:.1f} KB stored"
        else:
            size_str = f"{file_size} B stored" if file_size else ""
        self._set_secondary(self._files_card, size_str)

        health_label = stats.get("health_label", "")
        score = stats.get("health_score", 0)
        self._find_child_value(self._health_card, f"{score}")
        self._set_secondary(self._health_card, health_label)

        self._find_child_value(self._passwords_card, str(stats.get("password_count", 0)))
        self._find_child_value(self._notes_card, str(stats.get("note_count", 0)))
        self._find_child_value(self._files_card, str(stats.get("file_count", 0)))

    def _set_secondary(self, card: QFrame, text: str) -> None:
        label = card.findChild(QLabel, "stat_secondary")
        if label:
            label.setText(text)

    def _find_child_value(self, card: QFrame, value: str) -> None:
        label = card.findChild(QLabel, "stat_value")
        if label:
            label.setText(value)

    def update_activity(self, entries: list[dict]) -> None:
        """Update the recent activity list with audit log entries."""
        self._activity_list.clear()
        if not entries:
            self._activity_list.addItem(QListWidgetItem("No recent activity to display."))
            return
        for entry in entries:
            timestamp = entry.get("created_at", "")
            if timestamp:
                timestamp = str(timestamp)[:19]
            action = entry.get("action", "unknown")
            entity_type = entry.get("entity_type", "")
            entity_id = entry.get("entity_id", "")
            display = f"{timestamp}  |  {action}"
            if entity_type:
                display += f"  |  {entity_type}"
            if entity_id:
                display += f"  ({entity_id})"
            item = QListWidgetItem(display)
            item.setForeground(Qt.GlobalColor.white)
            self._activity_list.addItem(item)

