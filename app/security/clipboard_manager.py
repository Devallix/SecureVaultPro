"""Clipboard manager with automatic clearing for SecureVault Pro.

Provides secure clipboard operations that automatically clear after a
configurable timeout to prevent clipboard exposure.
"""

import threading

import pyperclip

from app.core.constants import CLIPBOARD_CLEAR_SECONDS
from app.logging.logger import get_logger

logger = get_logger(__name__)


class ClipboardManager:
    """Manages clipboard operations with automatic clearing.

    Copies sensitive data to the clipboard and schedules automatic
    clearing after the configured timeout.
    """

    def __init__(self, clear_seconds: int = CLIPBOARD_CLEAR_SECONDS) -> None:
        self._clear_seconds = clear_seconds
        self._clear_timer: threading.Timer | None = None
        self._lock = threading.Lock()

    def copy_secret(self, secret: str, label: str = "secret") -> None:
        """Copy a secret to the clipboard with auto-clear scheduling.

        Args:
            secret: The secret text to copy.
            label: Label for logging (does not log the actual secret).
        """
        with self._lock:
            self._cancel_pending_clear()

            try:
                pyperclip.copy(secret)
                logger.info("Copied {label} to clipboard (auto-clear in {secs}s)", label=label, secs=self._clear_seconds)
            except Exception:
                logger.warning("Failed to copy to clipboard")
                return

            self._clear_timer = threading.Timer(self._clear_seconds, self._clear_clipboard)
            self._clear_timer.daemon = True
            self._clear_timer.start()

    def clear(self) -> None:
        """Immediately clear the clipboard."""
        with self._lock:
            self._cancel_pending_clear()
            self._clear_clipboard()

    def _clear_clipboard(self) -> None:
        """Internal clipboard clear operation."""
        try:
            current = pyperclip.paste()
            if current:
                pyperclip.copy("")
                logger.info("Clipboard cleared")
        except Exception:
            logger.debug("Could not clear clipboard (may be empty)")

    def _cancel_pending_clear(self) -> None:
        """Cancel any pending auto-clear timer."""
        if self._clear_timer is not None:
            self._clear_timer.cancel()
            self._clear_timer = None
