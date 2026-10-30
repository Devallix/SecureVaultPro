"""Report ViewModel."""

from PySide6.QtCore import QObject, QMetaObject, Qt, Signal, Slot

from app.workers.report_worker import ReportWorker
from app.workers.thread_pool import start_worker


class ReportViewModel(QObject):
    """ViewModel for the report generation view."""

    report_generated = Signal(str)
    report_finished = Signal()
    error_occurred = Signal(str)

    def __init__(
        self,
        report_service,
        password_service,
        audit_service,
        analysis_service,
        ssh_key_repo=None,
        api_key_repo=None,
        licence_repo=None,
        vault_key=None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._report_service = report_service
        self._password_service = password_service
        self._audit_service = audit_service
        self._analysis_service = analysis_service
        self._ssh_key_repo = ssh_key_repo
        self._api_key_repo = api_key_repo
        self._licence_repo = licence_repo
        self._vault_key = vault_key
        self._vault_id: str | None = None
        self._last_result: str | None = None
        self._last_error: str | None = None

    def set_vault(self, vault_id: str) -> None:
        self._vault_id = vault_id

    def generate_report(self, report_type: str, output_path: str) -> None:
        """Generate a report of the given type in a background thread."""
        if self._vault_id is None:
            self.error_occurred.emit("No vault selected")
            return

        dispatch = {
            "passwords_csv": lambda: self._report_service.generate_passwords_csv(
                self._vault_id, output_path, self._password_service
            ),
            "passwords_excel": lambda: self._report_service.generate_passwords_excel(
                self._vault_id, output_path, self._password_service
            ),
            "passwords_pdf": lambda: self._report_service.generate_passwords_pdf(
                self._vault_id, output_path, self._password_service
            ),
            "audit_csv": lambda: self._report_service.generate_audit_csv(
                self._vault_id, output_path, self._audit_service
            ),
            "security_pdf": lambda: self._report_service.generate_security_report_pdf(
                self._vault_id, output_path, self._analysis_service
            ),
            "ssh_keys_csv": lambda: self._report_service.generate_ssh_keys_csv(
                self._vault_id, output_path, self._ssh_key_repo, self._vault_key
            ),
            "api_keys_csv": lambda: self._report_service.generate_api_keys_csv(
                self._vault_id, output_path, self._api_key_repo, self._vault_key
            ),
            "licences_csv": lambda: self._report_service.generate_licences_csv(
                self._vault_id, output_path, self._licence_repo, self._vault_key
            ),
        }

        func = dispatch.get(report_type)
        if func is None:
            self.error_occurred.emit(f"Unknown report type: {report_type}")
            return

        worker = ReportWorker(func)

        def on_result(val):
            self._last_result = output_path
            self._last_error = None

        def on_error(err):
            self._last_result = None
            self._last_error = str(err)

        def on_finished():
            QMetaObject.invokeMethod(
                self,
                "_dispatch_result",
                Qt.ConnectionType.QueuedConnection,
            )

        worker.signals.result.connect(on_result)
        worker.signals.error.connect(on_error)
        worker.signals.finished.connect(on_finished)
        start_worker(worker)

    @Slot()
    def _dispatch_result(self) -> None:
        error = self._last_error
        result = self._last_result
        self._last_result = None
        self._last_error = None

        if error:
            self.error_occurred.emit(error)
        elif result:
            self.report_generated.emit(result)
        self.report_finished.emit()
