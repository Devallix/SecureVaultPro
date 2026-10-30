"""Encryption worker for background file operations."""

from app.workers.base_worker import BaseWorker


class EncryptionWorker(BaseWorker):
    """Worker for encrypting files in the background."""

    def __init__(self, file_service, vault_id: str, file_path: str, output_dir: str) -> None:
        super().__init__()
        self._file_service = file_service
        self._vault_id = vault_id
        self._file_path = file_path
        self._output_dir = output_dir

    def run_task(self) -> dict:
        return self._file_service.encrypt_file(self._vault_id, self._file_path, self._output_dir)


class DecryptionWorker(BaseWorker):
    """Worker for decrypting files in the background."""

    def __init__(self, file_service, file_metadata_id: str, output_path: str) -> None:
        super().__init__()
        self._file_service = file_service
        self._file_metadata_id = file_metadata_id
        self._output_path = output_path

    def run_task(self) -> str:
        return self._file_service.decrypt_file(self._file_metadata_id, self._output_path)
