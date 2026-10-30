"""Platform-specific utilities for SecureVault Pro."""

import os
import platform
import sys


def is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system() == "Windows"


def is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system() == "Darwin"


def is_linux() -> bool:
    """Check if running on Linux."""
    return platform.system() == "Linux"


def get_platform_name() -> str:
    """Get a human-readable platform name."""
    system = platform.system()
    if system == "Windows":
        return f"Windows {platform.version()}"
    if system == "Darwin":
        return f"macOS {platform.mac_ver()[0]}"
    if system == "Linux":
        return f"Linux {platform.release()}"
    return system


def get_app_data_path() -> str:
    """Get the platform-appropriate application data path.

    Returns:
        Path string for application data storage.
    """
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
    elif system == "Darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    return base


def enable_high_dpi() -> None:
    """Enable high-DPI support before QApplication creation.

    Must be called before QApplication is instantiated.
    """
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    if hasattr(sys, "setrecursionlimit"):
        pass
