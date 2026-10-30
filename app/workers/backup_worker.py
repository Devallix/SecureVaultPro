"""Backup worker for background backup operations."""

from app.workers.base_worker import BaseWorker


class BackupWorker(BaseWorker):
    """Worker for creating backups in the background."""

    def __init__(self, backup_service) -> None:
        super().__init__()
        self._backup_service = backup_service

    def run_task(self) -> dict:
        return self._backup_service.create_backup()


class RestoreWorker(BaseWorker):
    """Worker for restoring backups in the background."""

    def __init__(self, backup_service, backup_path: str) -> None:
        super().__init__()
        self._backup_service = backup_service
        self._backup_path = backup_path

    def run_task(self) -> bool:
        return self._backup_service.restore_backup(self._backup_path)
