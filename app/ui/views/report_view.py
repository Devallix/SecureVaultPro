"""Report generation view."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

_REPORT_TYPES = {
    "passwords_csv": ("Passwords CSV", "passwords_export.csv", "CSV Files (*.csv)"),
    "passwords_excel": ("Passwords Excel", "passwords_export.xlsx", "Excel Files (*.xlsx)"),
    "passwords_pdf": ("Passwords PDF", "passwords_export.pdf", "PDF Files (*.pdf)"),
    "audit_csv": ("Audit Log CSV", "audit_log.csv", "CSV Files (*.csv)"),
    "security_pdf": ("Security Report PDF", "security_report.pdf", "PDF Files (*.pdf)"),
    "ssh_keys_csv": ("SSH Keys CSV", "ssh_keys_export.csv", "CSV Files (*.csv)"),
    "api_keys_csv": ("API Keys CSV", "api_keys_export.csv", "CSV Files (*.csv)"),
    "licences_csv": ("Software Licences CSV", "licences_export.csv", "CSV Files (*.csv)"),
}


class ReportView(QWidget):
    """Report generation panel with report type selection."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    @staticmethod
    def _theme_colors():
        from app.core.config import AppConfig
        is_dark = AppConfig().get("appearance.theme", "dark") == "dark"
        if is_dark:
            return {
                "card_bg": "#16162a",
                "card_border": "#2a2a4a",
                "text": "#e0e0e0",
                "text_muted": "#999",
                "group_text": "#ccc",
                "radio_bg": "#16162a",
                "radio_indicator": "#555",
                "radio_indicator_bg": "#1a1a2e",
                "gen_btn_text": "#1a1a2e",
                "accent": "#64B4FF",
            }
        else:
            return {
                "card_bg": "#ffffff",
                "card_border": "#d0d0d8",
                "text": "#1a1a2e",
                "text_muted": "#777",
                "group_text": "#555",
                "radio_bg": "transparent",
                "radio_indicator": "#aaa",
                "radio_indicator_bg": "#f5f5f7",
                "gen_btn_text": "#ffffff",
                "accent": "#3B82F6",
            }

    def refresh_theme(self) -> None:
        C = self._theme_colors()
        self._desc.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px;")
        self._group_box.setStyleSheet(
            f"QGroupBox {{ border: 1px solid {C['card_border']}; border-radius: 6px; "
            f"background: {C['card_bg']}; "
            f"margin-top: 12px; padding-top: 16px; font-size: 13px; color: {C['group_text']}; }}"
            "QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }"
        )
        for rb in self._radio_buttons.values():
            rb.setStyleSheet(
                f"QRadioButton {{ font-size: 13px; color: {C['text']}; spacing: 8px; background: {C['radio_bg']}; padding: 6px 8px; border-radius: 4px; }}"
                f"QRadioButton::indicator {{ width: 14px; height: 14px; border: 2px solid {C['radio_indicator']}; border-radius: 7px; background: {C['radio_indicator_bg']}; }}"
                "QRadioButton::indicator:checked { border: 2px solid #64B4FF; background: #64B4FF; }"
                "QRadioButton::indicator:hover { border: 2px solid #888; }"
            )
        self._generate_btn.setStyleSheet(
            f"QPushButton {{ background: #64B4FF; color: {C['gen_btn_text']}; border: none; border-radius: 6px; "
            "font-size: 13px; font-weight: bold; }"
            "QPushButton:hover { background: #82C4FF; }"
            "QPushButton:pressed { background: #4A9EE8; }"
        )

    def _build_ui(self) -> None:
        C = self._theme_colors()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Reports")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C['accent']};")
        layout.addWidget(title)

        self._desc = QLabel("Select a report type and click Generate to export data.")
        self._desc.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px;")
        layout.addWidget(self._desc)

        self._group_box = QGroupBox("Report Type")
        self._group_box.setStyleSheet(
            f"QGroupBox {{ border: 1px solid {C['card_border']}; border-radius: 6px; "
            f"background: {C['card_bg']}; "
            f"margin-top: 12px; padding-top: 16px; font-size: 13px; color: {C['group_text']}; }}"
            "QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }"
        )
        group_layout = QVBoxLayout(self._group_box)
        group_layout.setSpacing(8)

        self._radio_buttons: dict[str, QRadioButton] = {}
        first = True
        for key, (label, _, _) in _REPORT_TYPES.items():
            rb = QRadioButton(label)
            rb.setStyleSheet(
                f"QRadioButton {{ font-size: 13px; color: {C['text']}; spacing: 8px; background: {C['radio_bg']}; padding: 6px 8px; border-radius: 4px; }}"
                f"QRadioButton::indicator {{ width: 14px; height: 14px; border: 2px solid {C['radio_indicator']}; border-radius: 7px; background: {C['radio_indicator_bg']}; }}"
                "QRadioButton::indicator:checked { border: 2px solid #64B4FF; background: #64B4FF; }"
                "QRadioButton::indicator:hover { border: 2px solid #888; }"
            )
            if first:
                rb.setChecked(True)
                first = False
            self._radio_buttons[key] = rb
            group_layout.addWidget(rb)

        layout.addWidget(self._group_box)

        self._generate_btn = QPushButton("Generate Report")
        self._generate_btn.setFixedHeight(40)
        self._generate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._generate_btn.setStyleSheet(
            f"QPushButton {{ background: #64B4FF; color: {C['gen_btn_text']}; border: none; border-radius: 6px; "
            "font-size: 13px; font-weight: bold; }"
            "QPushButton:hover { background: #82C4FF; }"
            "QPushButton:pressed { background: #4A9EE8; }"
        )
        layout.addWidget(self._generate_btn)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet(f"color: {C['text_muted']}; font-size: 12px;")
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)

        layout.addStretch()

    def _selected_type(self) -> str | None:
        for key, rb in self._radio_buttons.items():
            if rb.isChecked():
                return key
        return None

    def get_selected_report_type(self) -> str | None:
        """Return the currently selected report type key."""
        return self._selected_type()

    def get_default_filename(self) -> str:
        """Return a sensible default filename for the selected type."""
        key = self._selected_type()
        if key and key in _REPORT_TYPES:
            return _REPORT_TYPES[key][1]
        return "report"

    def get_file_filter(self) -> str:
        """Return the file dialog filter for the selected type."""
        key = self._selected_type()
        if key and key in _REPORT_TYPES:
            return _REPORT_TYPES[key][2]
        return "All Files (*)"

    def set_status(self, message: str, success: bool = True) -> None:
        """Update the status label."""
        color = "#22C55E" if success else "#EF4444"
        self._status_label.setText(message)
        self._status_label.setStyleSheet(f"color: {color}; font-size: 12px;")

    def show_generating(self) -> None:
        """Show a generating status."""
        self._status_label.setText("Generating report...")
        self._status_label.setStyleSheet("color: #EAB308; font-size: 12px;")
        self._generate_btn.setEnabled(False)

    def show_complete(self) -> None:
        """Re-enable the generate button after completion."""
        self._generate_btn.setEnabled(True)
        self._status_label.setText("Report generation complete.")
        self._status_label.setStyleSheet("color: #22C55E; font-size: 12px;")
