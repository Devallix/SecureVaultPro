"""Markdown editor widget for SecureVault Pro."""

import re

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


def _theme_colors():
    from app.core.config import AppConfig
    is_dark = AppConfig().get("appearance.theme", "dark") == "dark"
    if is_dark:
        return {
            "bg": "#1a1a2e",
            "border": "#2a2a4a",
            "text": "#e0e0e0",
            "code_bg": "#0d0d1a",
            "muted": "#ccc",
        }
    else:
        return {
            "bg": "#ffffff",
            "border": "#d0d0d8",
            "text": "#1a1a2e",
            "code_bg": "#f5f5f7",
            "muted": "#666",
        }


def render_markdown(text: str) -> str:
    """Convert basic markdown text to HTML.

    Supports headers, bold, italic, inline code, code blocks,
    bullet lists, and links.
    """
    C = _theme_colors()

    lines = text.split("\n")
    html_lines: list[str] = []
    in_code_block = False

    for line in lines:
        if line.strip().startswith("```"):
            if in_code_block:
                html_lines.append("</pre></div>")
                in_code_block = False
            else:
                html_lines.append(f'<div style="background:{C["code_bg"]};border:1px solid {C["border"]};border-radius:4px;padding:8px;margin:4px 0;"><pre style="color:{C["text"]};font-family:Consolas,monospace;font-size:13px;margin:0;">')
                in_code_block = True
            continue

        if in_code_block:
            escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html_lines.append(escaped)
            continue

        stripped = line.strip()

        if stripped.startswith("### "):
            inner = _inline(stripped[4:])
            html_lines.append(f'<h3 style="color:#64B4FF;margin:8px 0 4px 0;">{inner}</h3>')
        elif stripped.startswith("## "):
            inner = _inline(stripped[3:])
            html_lines.append(f'<h2 style="color:#64B4FF;margin:10px 0 4px 0;">{inner}</h2>')
        elif stripped.startswith("# "):
            inner = _inline(stripped[2:])
            html_lines.append(f'<h1 style="color:#64B4FF;margin:12px 0 6px 0;">{inner}</h1>')
        elif stripped.startswith("- ") or stripped.startswith("* "):
            inner = _inline(stripped[2:])
            html_lines.append(
                f'<div style="color:{C["text"]};padding:2px 0 2px 16px;">'
                f'<span style="color:#64B4FF;">&#8226;</span> {inner}</div>'
            )
        elif stripped == "":
            html_lines.append("<br/>")
        else:
            inner = _inline(stripped)
            html_lines.append(f'<p style="color:{C["text"]};margin:4px 0;">{inner}</p>')

    if in_code_block:
        html_lines.append("</pre></div>")

    return "\n".join(html_lines)


def _inline(text: str) -> str:
    """Process inline markdown: bold, italic, code, links."""
    C = _theme_colors()
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Inline code
    text = re.sub(
        r'`([^`]+)`',
        rf'<code style="background:{C["code_bg"]};padding:2px 6px;border-radius:3px;font-family:Consolas,monospace;color:#F59E0B;">\1</code>',
        text,
    )
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', rf'<strong style="color:{C["text"]};">\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', rf'<em style="color:{C["muted"]};">\1</em>', text)
    # Links
    text = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        r'<a href="\2" style="color:#64B4FF;text-decoration:underline;">\1</a>',
        text,
    )
    return text


class MarkdownEditor(QWidget):
    """A split-pane markdown editor with live preview."""

    content_changed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._is_preview = False
        self._build_ui()

    def refresh_theme(self) -> None:
        C = _theme_colors()
        self._editor.setStyleSheet(
            f"QTextEdit {{ background: {C['bg']}; border: 1px solid {C['border']}; border-radius: 6px; color: {C['text']}; padding: 12px; }}"
        )
        self._preview.setStyleSheet(
            f"QTextBrowser {{ background: {C['bg']}; border: 1px solid {C['border']}; border-radius: 6px; padding: 12px; }}"
        )
        if self._is_preview:
            html = render_markdown(self._editor.toPlainText())
            self._preview.setHtml(
                f'<div style="font-family:Segoe UI,sans-serif;font-size:13px;">{html}</div>'
            )

    def _build_ui(self) -> None:
        C = _theme_colors()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)

        self._toggle_btn = QPushButton("Preview")
        self._toggle_btn.setFixedWidth(80)
        self._toggle_btn.setStyleSheet(
            "QPushButton { background: #3B82F6; color: white; border: none; border-radius: 4px; padding: 4px 8px; font-size: 11px; }"
            "QPushButton:hover { background: #2563EB; }"
        )
        self._toggle_btn.clicked.connect(self._toggle_mode)
        toolbar.addWidget(self._toggle_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self._editor = QTextEdit()
        self._editor.setPlaceholderText("Write your note in markdown...")
        self._editor.setFont(QFont("Consolas", 12))
        self._editor.setStyleSheet(
            f"QTextEdit {{ background: {C['bg']}; border: 1px solid {C['border']}; border-radius: 6px; color: {C['text']}; padding: 12px; }}"
        )
        self._editor.textChanged.connect(self.content_changed.emit)

        self._preview = QTextBrowser()
        self._preview.setOpenExternalLinks(True)
        self._preview.setStyleSheet(
            f"QTextBrowser {{ background: {C['bg']}; border: 1px solid {C['border']}; border-radius: 6px; padding: 12px; }}"
        )
        self._preview.setVisible(False)

        layout.addWidget(self._editor)
        layout.addWidget(self._preview)

    def _toggle_mode(self) -> None:
        self._is_preview = not self._is_preview
        if self._is_preview:
            html = render_markdown(self._editor.toPlainText())
            self._preview.setHtml(
                f'<div style="font-family:Segoe UI,sans-serif;font-size:13px;">{html}</div>'
            )
            self._editor.setVisible(False)
            self._preview.setVisible(True)
            self._toggle_btn.setText("Edit")
        else:
            self._preview.setVisible(False)
            self._editor.setVisible(True)
            self._toggle_btn.setText("Preview")

    def toPlainText(self) -> str:  # noqa: N802
        return self._editor.toPlainText()

    def setPlainText(self, text: str) -> None:  # noqa: N802
        self._editor.setPlainText(text)

    def clear(self) -> None:
        self._editor.clear()

    def setPlaceholderText(self, text: str) -> None:  # noqa: N802
        self._editor.setPlaceholderText(text)
