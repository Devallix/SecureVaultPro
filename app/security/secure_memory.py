"""Platform-specific secure memory utilities for SecureVault Pro.

Provides best-effort secure memory handling. On Windows, uses VirtualLock
to prevent sensitive data from being paged to disk. On Unix, uses mlock.
Falls back gracefully on unsupported platforms.
"""

import ctypes
import ctypes.util
import sys

from app.logging.logger import get_logger

logger = get_logger(__name__)

_IS_WINDOWS = sys.platform == "win32"
_IS_UNIX = sys.platform in ("linux", "darwin")


def lock_memory(data: bytearray | memoryview) -> bool:
    """Prevent memory region from being paged to disk.

    Args:
        data: The memory buffer to lock.

    Returns:
        True if the memory was successfully locked.
    """
    if _IS_WINDOWS:
        return _windows_lock(data)
    elif _IS_UNIX:
        return _unix_lock(data)
    return False


def unlock_memory(data: bytearray | memoryview) -> bool:
    """Unlock previously locked memory.

    Args:
        data: The memory buffer to unlock.

    Returns:
        True if the memory was successfully unlocked.
    """
    if _IS_WINDOWS:
        return _windows_unlock(data)
    elif _IS_UNIX:
        return _unix_unlock(data)
    return False


def secure_zero(data: bytearray) -> None:
    """Securely zero out a memory buffer.

    Attempts to use platform-specific secure zeroing to prevent
    compiler optimization from eliminating the operation.

    Args:
        data: The buffer to zero.
    """
    if _IS_WINDOWS:
        try:
            ctypes.windll.kernel32.RtlSecureZeroMemory(
                ctypes.addressof((ctypes.c_char * len(data)).from_buffer(data)),
                len(data),
            )
            return
        except Exception:
            pass

    for i in range(len(data)):
        data[i] = 0


def _windows_lock(data: bytearray | memoryview) -> bool:
    """Lock memory using Windows VirtualLock."""
    try:
        kernel32 = ctypes.windll.kernel32
        addr = ctypes.addressof((ctypes.c_char * len(data)).from_buffer(data))
        result = kernel32.VirtualLock(ctypes.c_void_p(addr), ctypes.c_size_t(len(data)))
        if result:
            logger.debug("Locked {size} bytes in memory (Windows)", size=len(data))
        return bool(result)
    except Exception as e:
        logger.debug("VirtualLock failed: {e}", e=str(e))
        return False


def _windows_unlock(data: bytearray | memoryview) -> bool:
    """Unlock memory using Windows VirtualUnlock."""
    try:
        kernel32 = ctypes.windll.kernel32
        addr = ctypes.addressof((ctypes.c_char * len(data)).from_buffer(data))
        result = kernel32.VirtualUnlock(ctypes.c_void_p(addr), ctypes.c_size_t(len(data)))
        return bool(result)
    except Exception:
        return False


def _unix_lock(data: bytearray | memoryview) -> bool:
    """Lock memory using POSIX mlock."""
    try:
        libc_name = ctypes.util.find_library("c")
        if libc_name is None:
            return False
        libc = ctypes.CDLL(libc_name)
        addr = ctypes.addressof((ctypes.c_char * len(data)).from_buffer(data))
        result = libc.mlock(ctypes.c_void_p(addr), ctypes.c_size_t(len(data)))
        if result == 0:
            logger.debug("Locked {size} bytes in memory (Unix)", size=len(data))
        return result == 0
    except Exception as e:
        logger.debug("mlock failed: {e}", e=str(e))
        return False


def _unix_unlock(data: bytearray | memoryview) -> bool:
    """Unlock memory using POSIX munlock."""
    try:
        libc_name = ctypes.util.find_library("c")
        if libc_name is None:
            return False
        libc = ctypes.CDLL(libc_name)
        addr = ctypes.addressof((ctypes.c_char * len(data)).from_buffer(data))
        result = libc.munlock(ctypes.c_void_p(addr), ctypes.c_size_t(len(data)))
        return result == 0
    except Exception:
        return False
