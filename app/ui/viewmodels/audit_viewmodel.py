"""Audit log ViewModel."""

from PySide6.QtCore import QObject, Signal


class AuditViewModel(QObject):
    """ViewModel for the audit log view."""

    entries_loaded = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, audit_service, parent=None) -> None:
        super().__init__(parent)
        self._service = audit_service
        self._vault_id: str | None = None

    def set_vault(self, vault_id: str) -> None:
        self._vault_id = vault_id
        self.load_entries()

    def load_entries(self) -> None:
        if self._vault_id is None:
            return
        try:
            entries = self._service.get_all(self._vault_id, limit=200)
            self.entries_loaded.emit(entries)
        except Exception as e:
            self.error_occurred.emit(str(e))
