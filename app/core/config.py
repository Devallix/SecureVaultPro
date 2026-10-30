"""Centralised configuration management for SecureVault Pro.

Handles application paths, database configuration, and runtime settings.
All paths are resolved relative to the user's home directory.
"""

import json
from pathlib import Path
from typing import Any

from app.core.constants import (
    APP_DIR_NAME,
    APP_NAME,
    AUTO_LOCK_TIMEOUT_SECONDS,
    BACKUPS_DIR_NAME,
    DATA_DIR_NAME,
    DATABASE_NAME,
    LOGS_DIR_NAME,
    TEMP_DIR_NAME,
)


class AppConfig:
    """Application configuration singleton.

    Manages directory paths, database settings, and runtime configuration.
    Configuration is persisted as JSON in the app data directory.
    """

    _instance: "AppConfig | None" = None
    _initialized: bool = False

    def __new__(cls) -> "AppConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True

        self._home_dir: Path = Path.home()
        self._app_data_dir: Path = self._home_dir / APP_DIR_NAME
        self._config_file: Path = self._app_data_dir / "config.json"

        self._ensure_directories()
        self._settings: dict[str, Any] = self._load_settings()

    @property
    def app_data_dir(self) -> Path:
        """Root application data directory."""
        return self._app_data_dir

    @property
    def data_dir(self) -> Path:
        """Database and vault data directory."""
        return self._app_data_dir / DATA_DIR_NAME

    @property
    def database_path(self) -> Path:
        """Full path to the SQLite database file."""
        return self.data_dir / DATABASE_NAME

    @property
    def logs_dir(self) -> Path:
        """Log files directory."""
        return self._app_data_dir / LOGS_DIR_NAME

    @property
    def backups_dir(self) -> Path:
        """Backup files directory."""
        return self._app_data_dir / BACKUPS_DIR_NAME

    @property
    def temp_dir(self) -> Path:
        """Temporary files directory."""
        return self._app_data_dir / TEMP_DIR_NAME

    @property
    def config_file(self) -> Path:
        """Path to the JSON configuration file."""
        return self._config_file

    @property
    def auto_lock_timeout(self) -> int:
        """Auto-lock timeout in seconds."""
        return self.get("security.auto_lock_timeout", AUTO_LOCK_TIMEOUT_SECONDS)

    @property
    def database_url(self) -> str:
        """SQLAlchemy-compatible database URL."""
        return f"sqlite:///{self.database_path}"

    @property
    def theme(self) -> str:
        """Current UI theme name."""
        return self.get("appearance.theme", "dark")

    @property
    def clipboard_clear_seconds(self) -> int:
        """Seconds before clipboard is cleared."""
        return self.get("security.clipboard_clear_seconds", 30)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a nested setting by dot-separated key.

        Args:
            key: Dot-separated key path (e.g., 'security.auto_lock_timeout').
            default: Value to return if key is not found.

        Returns:
            The setting value, or default if not found.
        """
        keys = key.split(".")
        value: Any = self._settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a nested setting by dot-separated key and persist.

        Args:
            key: Dot-separated key path.
            value: Value to set.
        """
        keys = key.split(".")
        target = self._settings
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        self._save_settings()

    def to_dict(self) -> dict[str, Any]:
        """Return a copy of all settings."""
        return dict(self._settings)

    def _ensure_directories(self) -> None:
        """Create all required application directories."""
        for directory in [
            self._app_data_dir,
            self._app_data_dir / DATA_DIR_NAME,
            self._app_data_dir / LOGS_DIR_NAME,
            self._app_data_dir / BACKUPS_DIR_NAME,
            self._app_data_dir / TEMP_DIR_NAME,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_settings(self) -> dict[str, Any]:
        """Load settings from disk, returning defaults if not found."""
        if self._config_file.exists():
            try:
                with open(self._config_file, encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except (json.JSONDecodeError, OSError):
                pass
        return self._default_settings()

    def _save_settings(self) -> None:
        """Persist current settings to disk."""
        try:
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    @staticmethod
    def _default_settings() -> dict[str, Any]:
        """Return default application settings."""
        return {
            "general": {
                "app_name": APP_NAME,
                "language": "en",
                "check_updates": True,
            },
            "appearance": {
                "theme": "dark",
                "font_size": 12,
                "animations_enabled": True,
            },
            "security": {
                "auto_lock_timeout": AUTO_LOCK_TIMEOUT_SECONDS,
                "clipboard_clear_seconds": 30,
                "max_login_attempts": 4,
                "lock_on_minimize": False,
                "lock_on_screen_saver": True,
            },
            "vault": {
                "default_crypto_version": 1,
                "password_history_count": 20,
                "password_expiry_days": 90,
            },
            "backup": {
                "auto_backup_enabled": False,
                "auto_backup_interval_hours": 24,
                "max_backup_versions": 10,
            },
            "notifications": {
                "enabled": True,
                "password_expiry_warning_days": 14,
            },
            "updates": {
                "endpoint": "https://github.com/Devallix/SecureVaultPro/raw/refs/heads/main/manifest.json",
                "check_enabled": True,
            },
        }
