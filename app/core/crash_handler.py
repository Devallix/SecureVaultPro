"""Crash handler for SecureVault Pro.

Captures uncaught exceptions, logs them securely (without leaking secrets),
and displays a user-friendly crash dialog before exit.
"""

import sys
import traceback
from typing import Any

from PySide6.QtWidgets import QApplication, QMessageBox

from app.core.constants import APP_NAME
from app.logging.logger import get_logger

logger = get_logger(__name__)

_SENSITIVE_PATTERNS = [
    "password",
    "master_key",
    "vault_key",
    "private_key",
    "secret",
    "token",
    "api_key",
]


def _sanitize_traceback(tb_text: str) -> str:
    """Remove potentially sensitive values from traceback text.

    Args:
        tb_text: Raw traceback string.

    Returns:
        Sanitized traceback string.
    """
    lines = tb_text.split("\n")
    sanitized = []
    for line in lines:
        lower = line.lower()
        if any(pattern in lower for pattern in _SENSITIVE_PATTERNS):
            sanitized.append(line.split("=")[0] + "= [REDACTED]" if "=" in line else "[REDACTED]")
        else:
            sanitized.append(line)
    return "\n".join(sanitized)


def _handle_exception(exc_type: type, exc_value: BaseException, exc_traceback: Any) -> None:
    """Global exception handler for uncaught exceptions.

    Args:
        exc_type: Exception class.
        exc_value: Exception instance.
        exc_traceback: Traceback object.
    """
    if exc_type is SystemExit:
        sys.exit(0)

    if exc_type is KeyboardInterrupt:
        sys.exit(0)

    tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    sanitized = _sanitize_traceback(tb_text)

    logger.critical(
        "Uncaught exception: {exc_type}: {exc_value}\n{traceback}",
        exc_type=exc_type.__name__,
        exc_value=str(exc_value),
        traceback=sanitized,
    )

    try:
        app = QApplication.instance()
        if app is not None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle(f"{APP_NAME} - Unexpected Error")
            msg.setText(f"An unexpected error occurred and {APP_NAME} must close.")
            msg.setInformativeText(
                f"Error: {exc_type.__name__}: {str(exc_value)[:200]}\n\n"
                "The error has been logged. Please restart the application."
            )
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
    except Exception:
        pass

    sys.exit(1)


def install_crash_handler() -> None:
    """Install the global exception hook."""
    sys.excepthook = _handle_exception
    logger.info("Crash handler installed")
