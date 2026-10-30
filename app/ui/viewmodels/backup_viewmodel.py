"""Backup ViewModel."""

from PySide6.QtCore import QObject, Signal


class BackupViewModel(QObject):
    """ViewModel for the backup view."""

    backups_loaded = Signal(list)
    backup_created = Signal(str)
    backup_restored = Signal(bool)
    backup_deleted = Signal(bool)
    error_occurred = Signal(str)

    def __init__(self, backup_service, parent=None) -> None:
        super().__init__(parent)
        self._service = backup_service
        self._vault_id: str | None = None

    def set_vault(self, vault_id: str) -> None:
        self._vault_id = vault_id
        self.load_backups()

    def load_backups(self) -> None:
        if self._vault_id is None:
            return
        try:
            backups = self._service.list_backups()
            self.backups_loaded.emit(backups)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def create_backup(self) -> None:
        if self._vault_id is None:
            return
        try:
            result = self._service.create_backup()
            self.backup_created.emit(result.get("filename", ""))
            self.load_backups()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def restore_backup(self, backup_path: str) -> None:
        try:
            success = self._service.restore_backup(backup_path)
            self.backup_restored.emit(success)
            if success:
                self.load_backups()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def delete_backup(self, backup_path: str) -> None:
        try:
            success = self._service.delete_backup(backup_path)
            self.backup_deleted.emit(success)
            if success:
                self.load_backups()
        except Exception as e:
            self.error_occurred.emit(str(e))
