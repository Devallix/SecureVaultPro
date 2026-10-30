"""Logging configuration for SecureVault Pro.

Uses Loguru for structured logging with security-aware filters that
prevent sensitive data (passwords, keys, tokens) from being written to logs.
"""

import re
import sys
from typing import Any

from loguru import logger as _loguru_logger

from app.core.config import AppConfig

_SENSITIVE_PATTERNS = re.compile(
    r"(password|passwd|pwd|secret|key|token|api_key|master_key|vault_key|"
    r"private_key|encryption_key|salt|nonce|credential|auth)[\"':\s]*[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)

_REDACTED = r"\1=[REDACTED]"


class SecurityFilter:
    """Loguru filter that redacts sensitive data from log messages."""

    def __call__(self, record: dict[str, Any]) -> bool:
        """Filter and sanitize log record data.

        Args:
            record: Loguru log record dictionary.

        Returns:
            True to allow the record, False to suppress.
        """
        message = record.get("message", "")
        record["message"] = _SENSITIVE_PATTERNS.sub(_REDACTED, str(message))

        extra = record.get("extra", {})
        for key, value in extra.items():
            if isinstance(value, str) and _SENSITIVE_PATTERNS.search(str(value)):
                extra[key] = "[REDACTED]"

        return True


def setup_logging() -> None:
    """Configure Loguru logging with file rotation and security filters."""
    _loguru_logger.remove()

    config = AppConfig()

    if sys.stderr is not None:
        _loguru_logger.add(
            sys.stderr,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
            level="INFO",
            colorize=True,
            filter=SecurityFilter(),
        )

    log_file = config.logs_dir / "securevault_{time:YYYY-MM-DD}.log"
    _loguru_logger.add(
        str(log_file),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        filter=SecurityFilter(),
    )

    error_file = config.logs_dir / "errors_{time:YYYY-MM-DD}.log"
    _loguru_logger.add(
        str(error_file),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="00:00:00",
        retention="7 days",
        compression="zip",
        encoding="utf-8",
        filter=SecurityFilter(),
    )

    _loguru_logger.info("Logging initialized")


def get_logger(name: str) -> Any:
    """Get a named logger instance.

    Args:
        name: Module name for the logger.

    Returns:
        Loguru logger bound to the given module name.
    """
    return _loguru_logger.bind(module=name)
