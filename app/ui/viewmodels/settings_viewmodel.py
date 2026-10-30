"""Settings ViewModel."""

from PySide6.QtCore import QObject, Signal

from app.core.config import AppConfig


class SettingsViewModel(QObject):
    """ViewModel for the settings view."""

    settings_loaded = Signal(dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._config = AppConfig()

    def load_settings(self) -> None:
        self.settings_loaded.emit(self._config.to_dict())

    def save_setting(self, key: str, value) -> None:
        self._config.set(key, value)

    def get_setting(self, key: str, default=None):
        return self._config.get(key, default)
