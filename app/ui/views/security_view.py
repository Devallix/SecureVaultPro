"""Security centre view."""

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class SecurityView(QWidget):
    """Security analysis and recommendations view."""

    analyse_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    @staticmethod
    def _theme_colors():
        from app.core.config import AppConfig
        is_dark = AppConfig().get("appearance.theme", "dark") == "dark"
        if is_dark:
            return {
                "accent": "#EF4444",
                "card_bg": "#16162a",
                "card_border": "#2a2a4a",
                "text_muted": "#aaa",
                "text": "#e0e0e0",
                "rec_bg": "#16162a",
                "rec_text": "#ccc",
            }
        else:
            return {
                "accent": "#DC2626",
                "card_bg": "#ffffff",
                "card_border": "#d0d0d8",
                "text_muted": "#666",
                "text": "#1a1a2e",
                "rec_bg": "#ffffff",
                "rec_text": "#333",
            }

    def refresh_theme(self) -> None:
        C = self._theme_colors()
        for card in self._cards:
            card.setStyleSheet(
                f"QFrame {{ background: {C['card_bg']}; border: 1px solid {C['card_border']}; border-radius: 8px; padding: 12px; }}"
            )
            val_label = card.findChild(QLabel, "card_value")
            if val_label:
                val_label.setStyleSheet(f"color: {C['text']};")
        self._rec_label.setStyleSheet(f"color: {C['text_muted']}; margin-top: 8px;")
        self._rec_text.setStyleSheet(
            f"QTextEdit {{ background: {C['rec_bg']}; border: 1px solid {C['card_border']}; border-radius: 8px; "
            f"color: {C['rec_text']}; padding: 12px; font-size: 12px; }}"
        )

    def _build_ui(self) -> None:
        C = self._theme_colors()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Security Centre")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C['accent']};")
        header.addWidget(title)
        header.addStretch()

        scan_btn = QPushButton("Run Security Scan")
        scan_btn.setStyleSheet(
            "QPushButton { background: #EF4444; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #DC2626; }"
        )
        scan_btn.clicked.connect(self.analyse_requested.emit)
        self._scan_btn = scan_btn
        header.addWidget(scan_btn)
        layout.addLayout(header)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)
        self._health_card = self._create_card("Overall Health", "---", "#8B5CF6", C)
        self._weak_card = self._create_card("Weak Passwords", "0", "#EF4444", C)
        self._old_card = self._create_card("Old Passwords", "0", "#F59E0B", C)
        self._dup_card = self._create_card("Duplicate Passwords", "0", "#F97316", C)
        self._cards = [self._health_card, self._weak_card, self._old_card, self._dup_card]
        cards_layout.addWidget(self._health_card)
        cards_layout.addWidget(self._weak_card)
        cards_layout.addWidget(self._old_card)
        cards_layout.addWidget(self._dup_card)
        layout.addLayout(cards_layout)

        self._rec_label = QLabel("Recommendations")
        self._rec_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self._rec_label.setStyleSheet(f"color: {C['text_muted']}; margin-top: 8px;")
        layout.addWidget(self._rec_label)

        self._rec_text = QTextEdit()
        self._rec_text.setReadOnly(True)
        self._rec_text.setMaximumHeight(160)
        self._rec_text.setStyleSheet(
            f"QTextEdit {{ background: {C['rec_bg']}; border: 1px solid {C['card_border']}; border-radius: 8px; "
            f"color: {C['rec_text']}; padding: 12px; font-size: 12px; }}"
        )
        self._rec_text.setPlaceholderText("Run a scan to see recommendations...")
        layout.addWidget(self._rec_text)

        layout.addStretch()

    def show_scanning(self) -> None:
        self._scan_btn.setEnabled(False)
        self._scan_btn.setText("Scanning...")
        self._rec_text.setPlainText("Running security analysis, please wait...")

    def _create_card(self, title: str, value: str, color: str, C: dict) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background: {C['card_bg']}; border: 1px solid {C['card_border']}; border-radius: 8px; padding: 12px; }}"
        )
        card.setFixedHeight(90)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        label = QLabel(title)
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")
        layout.addWidget(label)

        val_label = QLabel(value)
        val_label.setObjectName("card_value")
        val_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        val_label.setStyleSheet(f"color: {C['text']};")
        layout.addWidget(val_label)

        layout.addStretch()
        return card

    def update_analysis(self, result: dict) -> None:
        """Update the view with analysis results."""
        self._scan_btn.setEnabled(True)
        self._scan_btn.setText("Run Security Scan")
        self._set_card_value(self._health_card, f"{result.get('health_score', 0)}%")
        self._set_card_value(self._weak_card, str(len(result.get("weak_passwords", []))))
        self._set_card_value(self._old_card, str(len(result.get("old_passwords", []))))
        self._set_card_value(self._dup_card, str(len(result.get("duplicate_passwords", []))))

        recommendations = result.get("recommendations", [])
        if recommendations:
            self._rec_text.setPlainText("\n".join(f"  {r}" for r in recommendations))
        else:
            self._rec_text.setPlainText("No issues found. Your vault is healthy!")

    def _set_card_value(self, card: QFrame, value: str) -> None:
        label = card.findChild(QLabel, "card_value")
        if label:
            label.setText(value)
