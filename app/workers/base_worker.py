"""Base worker for background tasks using QRunnable."""

from PySide6.QtCore import QObject, QRunnable, Signal


class WorkerSignals(QObject):
    """Signals emitted by background workers."""

    started = Signal()
    finished = Signal()
    error = Signal(str)
    result = Signal(object)
    progress = Signal(int)


class BaseWorker(QRunnable):
    """Base class for background task workers.

    Subclasses implement the `run_task()` method.
    """

    def __init__(self) -> None:
        super().__init__()
        self.signals = WorkerSignals()
        self._is_cancelled = False

    def run(self) -> None:
        """Execute the worker task."""
        self.signals.started.emit()
        try:
            result = self.run_task()
            if not self._is_cancelled:
                self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

    def run_task(self) -> object:
        """Override this method to implement the task.

        Returns:
            Task result.
        """
        raise NotImplementedError

    def cancel(self) -> None:
        """Request cancellation of the worker."""
        self._is_cancelled = True
