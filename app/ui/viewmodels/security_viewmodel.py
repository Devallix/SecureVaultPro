"""Security centre ViewModel."""

from PySide6.QtCore import QObject, Signal

from app.workers.analysis_worker import AnalysisWorker
from app.workers.thread_pool import start_worker


class SecurityViewModel(QObject):
    """ViewModel for the security analysis view."""

    analysis_complete = Signal(dict)
    analysis_started = Signal()
    error_occurred = Signal(str)

    def __init__(self, analysis_service, parent=None) -> None:
        super().__init__(parent)
        self._service = analysis_service
        self._vault_id: str | None = None

    def set_vault(self, vault_id: str) -> None:
        self._vault_id = vault_id

    def run_analysis(self) -> None:
        if self._vault_id is None:
            return
        self.analysis_started.emit()
        worker = AnalysisWorker(self._service, self._vault_id)
        worker.signals.result.connect(self._on_analysis_done)
        worker.signals.error.connect(lambda err: self.error_occurred.emit(err))
        start_worker(worker)

    def _on_analysis_done(self, result: dict) -> None:
        self.analysis_complete.emit(result)
