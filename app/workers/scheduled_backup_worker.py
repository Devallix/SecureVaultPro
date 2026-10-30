"""Scheduled backup worker using QTimer for periodic auto-backup."""

from datetime import datetime

from PySide6.QtCore import QObject, QTimer, Signal

from app.core.config import AppConfig
from app.logging.logger import get_logger

logger = get_logger(__name__)


class ScheduledBackupWorker(QObject):
    """Periodically checks if an automatic backup is due and triggers it.

    Uses a QTimer to poll every 60 seconds. Compares elapsed time since
    the last backup against the configured interval threshold.
    """

    backup_created = Signal(dict)
    backup_error = Signal(str)

    CHECK_INTERVAL_MS = 60_000

    def __init__(self, backup_service, parent=None) -> None:
        super().__init__(parent)
        self._backup_service = backup_service
        self._last_backup_time: datetime | None = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check_backup_due)
        self._running = False

    def start(self) -> None:
        """Start the periodic backup check."""
        if self._running:
            return
        self._running = True
        self._last_backup_time = datetime.now()
        self._timer.start(self.CHECK_INTERVAL_MS)
        logger.info("Scheduled backup worker started (interval check: {ms}ms)", ms=self.CHECK_INTERVAL_MS)

    def stop(self) -> None:
        """Stop the periodic backup check."""
        self._timer.stop()
        self._running = False
        logger.info("Scheduled backup worker stopped")

    def _check_backup_due(self) -> None:
        config = AppConfig()
        enabled = config.get("backup.auto_backup_enabled", False)
        if not enabled:
            return

        interval_hours = config.get("backup.auto_backup_interval_hours", 24)
        if self._last_backup_time is None:
            self._last_backup_time = datetime.now()
            return

        elapsed = (datetime.now() - self._last_backup_time).total_seconds() / 3600.0
        if elapsed < interval_hours:
            return

        logger.info("Auto-backup due (elapsed: {h:.1f}h, threshold: {th}h)", h=elapsed, th=interval_hours)
        try:
            result = self._backup_service.create_backup()
            self._last_backup_time = datetime.now()
            self.backup_created.emit(result)
        except Exception as e:
            logger.error("Auto-backup failed: {err}", err=str(e))
            self.backup_error.emit(str(e))
