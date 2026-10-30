"""Files ViewModel."""

from PySide6.QtCore import QObject, Signal


class FilesViewModel(QObject):
    """ViewModel for file encryption view."""

    files_loaded = Signal(list)
    file_operation_complete = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, file_service, parent=None) -> None:
        super().__init__(parent)
        self._service = file_service
        self._vault_id: str | None = None

    def set_vault(self, vault_id: str) -> None:
        self._vault_id = vault_id
        self.load_files()

    def load_files(self) -> None:
        if self._vault_id is None:
            return
        try:
            files = self._service.get_files(self._vault_id)
            self.files_loaded.emit(files)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def encrypt_file(self, file_path: str, output_dir: str, delete_original: bool = False) -> None:
        if self._vault_id is None:
            return
        try:
            result = self._service.encrypt_file(self._vault_id, file_path, output_dir, delete_original)
            self.file_operation_complete.emit(f"Encrypted: {result.get('original_name', '')}")
            self.load_files()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def encrypt_folder(self, folder_path: str, output_dir: str, delete_original: bool = False) -> None:
        if self._vault_id is None:
            return
        try:
            results = self._service.encrypt_folder(self._vault_id, folder_path, output_dir, delete_original)
            errors = [r for r in results if "error" in r]
            success_count = len(results) - len(errors)
            if errors:
                self.file_operation_complete.emit(
                    f"Encrypted {success_count} files, {len(errors)} failed"
                )
            else:
                self.file_operation_complete.emit(f"Encrypted {success_count} files")
            self.load_files()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def decrypt_file(self, file_metadata_id: str, output_path: str) -> None:
        try:
            self._service.decrypt_file(file_metadata_id, output_path)
            self.file_operation_complete.emit(f"Decrypted to: {output_path}")
        except Exception as e:
            self.error_occurred.emit(str(e))

    def delete_file(self, file_metadata_id: str) -> None:
        try:
            self._service.delete_file(file_metadata_id)
            self.load_files()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def delete_all_files(self) -> None:
        if self._vault_id is None:
            return
        try:
            count = self._service.delete_all_files(self._vault_id)
            self.file_operation_complete.emit(f"Deleted {count} encrypted files")
            self.load_files()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def decrypt_all_files(self, output_dir: str) -> None:
        if self._vault_id is None:
            return
        try:
            results = self._service.decrypt_all_files(self._vault_id, output_dir)
            errors = [r for r in results if "error" in r]
            success_count = len(results) - len(errors)
            if errors:
                self.file_operation_complete.emit(f"Decrypted {success_count} files, {len(errors)} failed")
            else:
                self.file_operation_complete.emit(f"Decrypted {success_count} files to {output_dir}")
            self.load_files()
        except Exception as e:
            self.error_occurred.emit(str(e))
