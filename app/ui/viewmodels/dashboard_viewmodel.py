"""Dashboard ViewModel for overview statistics."""

from PySide6.QtCore import QObject, Signal

from app.logging.logger import get_logger

logger = get_logger(__name__)


class DashboardViewModel(QObject):
    """ViewModel for the dashboard view."""

    stats_loaded = Signal(dict)
    activity_loaded = Signal(list)
    expiring_loaded = Signal(list)

    def __init__(self, password_repo, note_repo, file_repo, analysis_service, parent=None) -> None:
        super().__init__(parent)
        self._password_repo = password_repo
        self._note_repo = note_repo
        self._file_repo = file_repo
        self._analysis_service = analysis_service
        self._audit_service = None
        self._password_service = None
        self._vault_id: str | None = None

    def set_audit_service(self, audit_service) -> None:
        """Set the audit service for recent activity queries."""
        self._audit_service = audit_service

    def set_password_service(self, password_service) -> None:
        """Set the password service for decrypting expiring entry titles."""
        self._password_service = password_service

    def load_stats(self, vault_id: str) -> None:
        self._vault_id = vault_id
        try:
            password_count = self._password_repo.count_by_vault(vault_id)
        except Exception as e:
            logger.warning("Failed to count passwords: {}", e)
            password_count = 0

        try:
            note_count = self._note_repo.count_by_vault(vault_id)
        except Exception as e:
            logger.warning("Failed to count notes: {}", e)
            note_count = 0

        try:
            file_count = self._file_repo.count_by_vault(vault_id)
        except Exception as e:
            logger.warning("Failed to count files: {}", e)
            file_count = 0

        try:
            total_file_size = self._file_repo.total_size_by_vault(vault_id)
        except Exception as e:
            logger.warning("Failed to get total file size: {}", e)
            total_file_size = 0

        weak_count = 0
        expired_count = 0
        health_score = 0
        if self._analysis_service:
            try:
                result = self._analysis_service.analyse_vault(vault_id)
                health_score = result.get("health_score", 0)
                weak_count = len(result.get("weak_passwords", []))
                expired_count = len(result.get("old_passwords", []))
            except Exception as e:
                logger.warning("Failed to analyse vault: {}", e)

        if health_score >= 80:
            health_label = "Good"
        elif health_score >= 50:
            health_label = "Fair"
        else:
            health_label = "Poor"

        stats = {
            "password_count": password_count,
            "note_count": note_count,
            "file_count": file_count,
            "total_file_size": total_file_size,
            "health_score": health_score,
            "weak_count": weak_count,
            "expired_count": expired_count,
            "health_label": health_label,
        }
        self.stats_loaded.emit(stats)

    def load_recent_activity(self, vault_id: str) -> None:
        """Fetch the last 10 audit log entries for the dashboard."""
        if self._audit_service is None:
            self.activity_loaded.emit([])
            return
        try:
            entries = self._audit_service.get_all(vault_id, limit=10)
            self.activity_loaded.emit(entries)
        except Exception:
            self.activity_loaded.emit([])

    def load_expiring(self, vault_id: str, days: int = 14) -> None:
        """Fetch passwords expiring within the given number of days."""
        try:
            entries = self._password_repo.get_expiring_soon(vault_id, days)
            result = []
            for e in entries:
                if self._password_service:
                    entry_data = self._password_service.get_password(e.id)
                    title = entry_data.get("title", "") if entry_data else f"Password ({e.id[:8]})"
                else:
                    title = f"Password ({e.id[:8]})"
                result.append({
                    "id": e.id,
                    "title": title,
                    "expires_at": e.expires_at.isoformat() if e.expires_at else None,
                })
            self.expiring_loaded.emit(result)
        except Exception:
            self.expiring_loaded.emit([])
