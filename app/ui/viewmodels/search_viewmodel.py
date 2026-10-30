"""Search ViewModel for global vault search."""

from PySide6.QtCore import QObject, Signal


class SearchViewModel(QObject):
    """ViewModel for the global search functionality."""

    results_loaded = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, search_service, parent=None) -> None:
        super().__init__(parent)
        self._service = search_service
        self._vault_id: str | None = None

    def set_vault(self, vault_id: str) -> None:
        self._vault_id = vault_id

    def search(self, query: str) -> None:
        """Perform a global search across all vault entities."""
        if self._vault_id is None or not query.strip():
            self.results_loaded.emit([])
            return
        try:
            results = self._service.search(self._vault_id, query)
            self.results_loaded.emit(results)
        except Exception as e:
            self.error_occurred.emit(str(e))
