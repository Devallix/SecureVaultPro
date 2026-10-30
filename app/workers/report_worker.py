"""Report generation worker for background report creation."""

from app.workers.base_worker import BaseWorker


class ReportWorker(BaseWorker):
    """Worker for generating reports in the background."""

    def __init__(self, report_func, *args, **kwargs) -> None:
        super().__init__()
        self._report_func = report_func
        self._args = args
        self._kwargs = kwargs

    def run_task(self) -> str:
        return self._report_func(*self._args, **self._kwargs)
