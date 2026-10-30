"""Background worker for SecureVault Pro update checks and downloads.

Wraps :class:`app.core.updates.updater.UpdateService` in a QRunnable so the
UI never blocks while contacting the manifest endpoint or downloading a
release ZIP. Emits PySide6 signals for progress and completion.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Signal

from app.core.updates.manifest import Manifest
from app.core.updates.updater import UpdateService


class UpdateWorkerSignals(QObject):
    """Signals emitted by :class:`UpdateWorker`."""

    started = Signal()
    finished = Signal()
    error = Signal(str)
    update_available = Signal(object)  # Manifest
    update_not_available = Signal()
    download_progress = Signal(int)  # percent 0-100
    download_complete = Signal(str)  # path to zip
    install_ready = Signal(str)  # path to swap batch


class UpdateWorker(QRunnable):
    """QRunnable that checks for or downloads an update in a background thread."""

    def __init__(
        self,
        service: UpdateService,
        action: str = "check",
        endpoint: str | None = None,
        download_url: str | None = None,
        expected_sha256: str | None = None,
    ) -> None:
        super().__init__()
        self._service = service
        self._action = action
        self._endpoint = endpoint
        self._download_url = download_url
        self._expected_sha256 = expected_sha256
        self.signals = UpdateWorkerSignals()
        self._is_cancelled = False

    def run(self) -> None:
        """Execute the update task."""
        self.signals.started.emit()
        try:
            if self._action == "check":
                self._run_check()
            elif self._action == "download":
                self._run_download()
            else:
                raise ValueError(f"Unknown update worker action: {self._action}")
        except Exception as exc:  # noqa: BLE001
            self.signals.error.emit(str(exc))
        finally:
            if not self._is_cancelled:
                self.signals.finished.emit()

    def _run_check(self) -> None:
        manifest = self._service.check_for_updates(endpoint=self._endpoint)
        if manifest is None:
            self.signals.update_not_available.emit()
        else:
            self.signals.update_available.emit(manifest)

    def _run_download(self) -> None:
        url = self._download_url or self._endpoint
        if not url:
            self.signals.error.emit("No download URL provided")
            return

        # Build a lightweight manifest-like object for the downloader.
        from app.core.updates.manifest import Version

        manifest = Manifest(
            version=Version(0, 0, 0),
            url=url,
            sha256=self._expected_sha256,
        )

        def progress(percent: int) -> None:
            if not self._is_cancelled:
                self.signals.download_progress.emit(percent)

        zip_path = self._service.download_update(manifest, progress_callback=progress)
        if not self._is_cancelled:
            self.signals.download_complete.emit(zip_path)

    def cancel(self) -> None:
        """Request cancellation of the worker."""
        self._is_cancelled = True
