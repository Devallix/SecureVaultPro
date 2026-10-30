"""Analysis worker for background security analysis."""

from app.workers.base_worker import BaseWorker


class AnalysisWorker(BaseWorker):
    """Worker for running security analysis in the background."""

    def __init__(self, analysis_service, vault_id: str) -> None:
        super().__init__()
        self._analysis_service = analysis_service
        self._vault_id = vault_id

    def run_task(self) -> dict:
        return self._analysis_service.analyse_vault(self._vault_id)
