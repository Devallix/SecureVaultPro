"""SecureVault Pro — Enterprise File Encryption & Password Management.

Entry point for the application. Initialises logging, crash handler,
dependency container, and launches the Qt application with splash screen.
"""

import os
import sys

if sys.platform == "win32":
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

from app.utils.platform_utils import enable_high_dpi

enable_high_dpi()

if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("securevault.pro.1.0")
    except Exception:
        pass

from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtGui import QFont, QIcon  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from app.core.app_container import get_container  # noqa: E402
from app.core.config import AppConfig  # noqa: E402
from app.core.constants import APP_NAME, APP_VERSION, SPLASH_DURATION_MS  # noqa: E402
from app.core.crash_handler import install_crash_handler  # noqa: E402
from app.core.updates.updater import UpdateService  # noqa: E402
from app.logging.logger import get_logger, setup_logging  # noqa: E402

logger = get_logger(__name__)


def _create_lock_icon() -> QIcon:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "resources", "icons", "vault.png")
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    return QIcon()


def _create_application() -> QApplication:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("SecureVault")
    app.setOrganizationDomain("securevault.app")
    app.setFont(QFont("Segoe UI", 10))
    app.setWindowIcon(_create_lock_icon())
    return app


def _init_services() -> None:
    container = get_container()
    config = AppConfig()
    container.register_instance(AppConfig, config)

    update_service = UpdateService(config=config, current_version=APP_VERSION)
    container.register_instance(UpdateService, update_service)

    from app.database.session_factory import create_all_tables, init_session_factory

    init_session_factory(config)
    create_all_tables()

    from app.core.session import SessionManager

    session = SessionManager()
    container.register_instance(SessionManager, session)


def _has_vault() -> bool:
    from app.database.session_factory import get_session
    from app.models.vault import Vault

    with get_session() as session:
        vault = session.query(Vault).first()
        return vault is not None


def main() -> None:
    setup_logging()
    install_crash_handler()
    logger.info("Starting {app} v{v}", app=APP_NAME, v=APP_VERSION)

    app = _create_application()
    _init_services()

    from app.ui.splash_screen import SplashScreen

    splash = SplashScreen()
    splash.show()
    splash.start_progress()
    app.processEvents()

    def _finish_splash() -> None:
        splash.finish()
        if _has_vault():
            _show_unlock(app)
        else:
            _show_create_vault(app)

    QTimer.singleShot(SPLASH_DURATION_MS, _finish_splash)

    sys.exit(app.exec())


def _show_create_vault(app: QApplication) -> None:
    from app.authentication.master_password import create_master_password
    from app.core.app_container import get_container
    from app.core.session import SessionManager
    from app.database.session_factory import get_session
    from app.models.vault import Vault
    from app.ui.dialogs.create_vault_dialog import CreateVaultDialog

    dialog = CreateVaultDialog()
    if dialog.exec():
        vault_name, password = dialog.get_data()
        vault_key, salt_hex, verify_hash = create_master_password(password)

        with get_session() as session:
            vault = Vault(
                name=vault_name,
                salt=salt_hex,
                verify_hash=verify_hash,
                is_locked=False,
                algorithm_version=1,
            )
            session.add(vault)
            session.commit()
            vault_id = vault.id

        from app.repositories.recovery_key_repository import RecoveryKeyRepository
        from app.services.recovery_key_service import RecoveryKeyService

        with get_session() as session:
            repo = RecoveryKeyRepository(session)
            service = RecoveryKeyService(repo)
            recovery_words = service.generate_and_store(vault_id, salt_hex, vault_key)
            session.commit()

        from app.ui.dialogs.recovery_key_display_dialog import RecoveryKeyDisplayDialog

        recovery_dialog = RecoveryKeyDisplayDialog(recovery_words)
        recovery_dialog.exec()

        container = get_container()
        session_mgr = container.resolve(SessionManager)
        session_mgr.unlock(vault_key, vault_id)
        _show_vault(app)
    else:
        app.quit()


def _show_unlock(app: QApplication) -> None:
    from app.core.app_container import get_container
    from app.core.session import SessionManager
    from app.ui.dialogs.unlock_dialog import UnlockDialog

    dialog = UnlockDialog()
    if dialog.exec():
        container = get_container()
        session_mgr = container.resolve(SessionManager)
        session_mgr.unlock(dialog.vault_key, dialog.vault_id)
        _show_vault(app)
    else:
        app.quit()


def _show_vault(app: QApplication) -> None:
    from app.core.app_container import get_container
    from app.core.session import SessionManager
    from app.ui.main_window import MainWindow

    container = get_container()
    session_mgr = container.resolve(SessionManager)
    window = MainWindow(vault_key=session_mgr.vault_key, vault_id=session_mgr.vault_id)

    def _on_vault_locked() -> None:
        _show_unlock(app)

    def _on_vault_deleted() -> None:
        _show_create_vault(app)

    window.vault_locked.connect(_on_vault_locked)
    window.vault_deleted.connect(_on_vault_deleted)
    window.showMaximized()


if __name__ == "__main__":
    main()
