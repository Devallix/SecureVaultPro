"""Secure file deletion utilities for SecureVault Pro.

Provides secure file overwriting before deletion to prevent data recovery.
Note: On SSDs with wear leveling, this is best-effort. Full disk encryption
is the recommended protection for SSDs.
"""

import os
from pathlib import Path

from app.core.exceptions import SecureDeleteError
from app.logging.logger import get_logger

logger = get_logger(__name__)

_OVERWRITE_PASSES = 3


def secure_delete_file(file_path: str | Path, passes: int = _OVERWRITE_PASSES) -> bool:
    """Securely delete a file by overwriting before removal.

    Args:
        file_path: Path to the file to delete.
        passes: Number of overwrite passes.

    Returns:
        True if the file was successfully deleted.

    Raises:
        SecureDeleteError: If the secure deletion fails.
    """
    path = Path(file_path)
    if not path.exists():
        logger.warning("File not found for secure deletion: {path}", path=str(path))
        return True

    if not path.is_file():
        raise SecureDeleteError(f"Not a regular file: {path}")

    try:
        file_size = path.stat().st_size

        with open(path, "r+b") as f:
            for pass_num in range(passes):
                f.seek(0)
                if pass_num % 2 == 0:
                    f.write(b"\x00" * file_size)
                else:
                    f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())

            if file_size < 1024:
                f.seek(0)
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())

        path.unlink()
        logger.debug("Securely deleted: {path}", path=str(path))
        return True

    except OSError as e:
        raise SecureDeleteError(f"Failed to securely delete {path}: {e}") from e


def secure_delete_directory(dir_path: str | Path) -> bool:
    """Securely delete all files in a directory, then remove the directory.

    Args:
        dir_path: Path to the directory to delete.

    Returns:
        True if successful.

    Raises:
        SecureDeleteError: If deletion fails.
    """
    path = Path(dir_path)
    if not path.exists():
        return True

    if not path.is_dir():
        raise SecureDeleteError(f"Not a directory: {path}")

    try:
        for item in path.rglob("*"):
            if item.is_file():
                secure_delete_file(item)

        path.rmdir()
        logger.debug("Securely deleted directory: {path}", path=str(path))
        return True

    except OSError as e:
        raise SecureDeleteError(f"Failed to securely delete directory {path}: {e}") from e
