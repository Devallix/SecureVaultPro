"""Theme manager for SecureVault Pro."""

from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.core.config import AppConfig
from app.logging.logger import get_logger

logger = get_logger(__name__)

THEMES_DIR = Path(__file__).parent


class ThemeManager:
    """Manages application theme switching (dark/light)."""

    _instance: "ThemeManager | None" = None

    def __new__(cls) -> "ThemeManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self._current_theme = "dark"

    def apply_theme(self, theme_name: str) -> None:
        """Apply a theme to the application.

        Args:
            theme_name: 'dark' or 'light'.
        """
        qss_file = THEMES_DIR / f"{theme_name}_theme.qss"
        if not qss_file.exists():
            logger.warning("Theme file not found: {path}", path=str(qss_file))
            return

        app = QApplication.instance()
        if app is None:
            return

        with open(qss_file, encoding="utf-8") as f:
            app.setStyleSheet(f.read())

        self._current_theme = theme_name
        config = AppConfig()
        config.set("appearance.theme", theme_name)
        logger.info("Theme applied: {theme}", theme=theme_name)

    @property
    def current_theme(self) -> str:
        """Get the current theme name."""
        return self._current_theme

    def toggle_theme(self) -> None:
        """Toggle between dark and light themes."""
        new_theme = "light" if self._current_theme == "dark" else "dark"
        self.apply_theme(new_theme)
