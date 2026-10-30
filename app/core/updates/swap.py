"""Swap batch script generation for SecureVault Pro updates.

The updater cannot replace its own executable while running, so it writes a
detached Windows batch file to the install folder's parent directory. That
batch file waits for the app to exit, renames the install folder aside,
extracts the new ZIP over the original path, relaunches the app, and
self-deletes. On failure it rolls back by restoring the previous folder.
"""

from __future__ import annotations

import os
from pathlib import Path


class SwapBatch:
    """Generated swap batch script and the paths it operates on."""

    def __init__(
        self,
        install_dir: str,
        zip_path: str,
        bat_path: str,
        old_dir: str,
        relaunch_target: str,
    ) -> None:
        self.install_dir = install_dir
        self.zip_path = zip_path
        self.bat_path = bat_path
        self.old_dir = old_dir
        self.relaunch_target = relaunch_target

    def write(self) -> str:
        """Write the batch script to disk and return its path."""
        content = self._batch_content()
        with open(self.bat_path, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(content)
        return self.bat_path

    def _batch_content(self) -> str:
        install_dir = self.install_dir.replace("/", "\\")
        zip_path = self.zip_path.replace("/", "\\")
        old_dir = self.old_dir.replace("/", "\\")
        relaunch_target = self.relaunch_target.replace("/", "\\")
        bat_dir = os.path.dirname(self.bat_path).replace("/", "\\")

        return f"""@echo off
setlocal enabledelayedexpansion

echo SecureVault Pro updater: installing update...
set "INSTALL_DIR={install_dir}"
set "ZIP_PATH={zip_path}"
set "OLD_DIR={old_dir}"
set "RELAUNCH={relaunch_target}"
set "BAT_DIR={bat_dir}"

:: Wait briefly for the main process to fully exit
timeout /t 3 /nobreak >nul

:: Rollback marker
set "ROLLBACK=0"

if not exist "%ZIP_PATH%" (
    echo ERROR: update zip not found.
    goto rollback
)

:: Rename the current install folder aside
if exist "%INSTALL_DIR%" (
    ren "%INSTALL_DIR%" "%OLD_DIR%" 2>nul
    if errorlevel 1 (
        echo ERROR: could not rename install folder.
        set ROLLBACK=1
        goto rollback
    )
)

:: Create a fresh install folder
mkdir "%INSTALL_DIR%" 2>nul
if errorlevel 1 (
    echo ERROR: could not create install folder.
    set ROLLBACK=1
    goto rollback
)

:: Extract the zip over the install folder using PowerShell
powershell -NoProfile -Command "& {{ Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('%ZIP_PATH%', '%INSTALL_DIR%') }}" 2>nul
if errorlevel 1 (
    echo ERROR: extraction failed.
    set ROLLBACK=1
    goto rollback
)

:: Clean up the downloaded zip
del "%ZIP_PATH%" 2>nul

:: Relaunch the application
if exist "%RELAUNCH%" (
    start "" "%RELAUNCH%"
) else (
    start "" cmd /c "cd /d "%BAT_DIR%" && python main.py"
)

:: Self-delete this batch file
goto selfdelete

:rollback
if "%ROLLBACK%"=="1" (
    echo Rolling back to previous version...
    if exist "%OLD_DIR%" (
        if exist "%INSTALL_DIR%" rmdir /s /q "%INSTALL_DIR%" 2>nul
        ren "%OLD_DIR%" "%INSTALL_DIR%" 2>nul
    )
)
echo Update failed. Previous version restored.

:selfdelete
del "%~f0" 2>nul
endlocal
"""

def generate_swap_batch(
    install_dir: str | Path,
    zip_path: str | Path,
    bat_path: str | Path,
    relaunch_target: str | Path | None = None,
) -> SwapBatch:
    """Generate and return a :class:`SwapBatch` for the given paths.

    Args:
        install_dir: The application install folder (to be replaced).
        zip_path: Path to the downloaded update ZIP.
        bat_path: Where to write the batch script.
        relaunch_target: Executable to relaunch after install. Defaults to
            ``SecureVaultPro.exe`` inside ``install_dir``, falling back to
            ``main.py`` in the same directory as the batch file.

    Returns:
        A populated :class:`SwapBatch` (not yet written to disk).
    """
    install_dir_str = str(install_dir)
    zip_path_str = str(zip_path)
    bat_path_str = str(bat_path)

    install_parent = str(Path(install_dir_str).parent)
    old_dir = str(Path(install_parent) / f"SecureVaultPro.old_{_timestamp()}")

    if relaunch_target is None:
        exe_candidate = Path(install_dir_str) / "SecureVaultPro.exe"
        if exe_candidate.exists():
            relaunch_target = str(exe_candidate)
        else:
            relaunch_target = str(Path(bat_path_str).parent / "main.py")

    return SwapBatch(
        install_dir=install_dir_str,
        zip_path=zip_path_str,
        bat_path=bat_path_str,
        old_dir=old_dir,
        relaunch_target=str(relaunch_target),
    )


def _timestamp() -> str:
    from datetime import datetime

    return datetime.now().strftime("%Y%m%d_%H%M%S")
