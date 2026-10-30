"""Build a release ZIP and generate the update manifest for SecureVault Pro.

This tool packages the application with PyInstaller, builds the release ZIP from
the bundled output, computes SHA-256 and size, stamps the publication timestamp,
and writes ``manifest.json`` to the project root.

Usage:

    python tools/build_update.py                                      # full build: PyInstaller -> zip -> manifest
    python tools/build_update.py --skip-build                         # re-zip existing dist without PyInstaller
    python tools/build_update.py --url "https://..."                  # set manifest URL
    python tools/build_update.py --notes "Release notes"              # set release notes
    python tools/build_update.py --url "..." --notes "..."            # set both

The edited URL and notes are preserved across rebuilds: the tool merges them
into an existing manifest.json if one exists.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

try:
    from app.core.constants import APP_VERSION
except ImportError:  # allow running without the package on the path
    APP_VERSION = "0.1.0"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = PROJECT_ROOT / "dist" / "SecureVaultPro"
RELEASES_DIR = PROJECT_ROOT / "releases"
MANIFEST_PATH = PROJECT_ROOT / "manifest.json"
SPEC_FILE = PROJECT_ROOT / "SecureVaultPro.spec"

CHUNK_SIZE = 64 * 1024


def _load_existing_manifest() -> dict:
    if MANIFEST_PATH.exists():
        try:
            with open(MANIFEST_PATH, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def _package_app() -> None:
    """Package the application using PyInstaller in onedir mode."""
    spec_path = SPEC_FILE
    if not spec_path.exists():
        # Create a default spec file if none exists
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("resources", "resources"),
        ("docs", "docs"),
    ],
    hiddenimports=[
        "app.core.config",
        "app.core.constants",
        "app.core.updates",
        "app.core.updates.manifest",
        "app.core.updates.updater",
        "app.core.updates.swap",
        "app.core.updates.version",
        "app.workers.update_worker",
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="SecureVaultPro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="resources/icons/vault.png",
)

app = BUNDLE(
    exe,
    name="SecureVaultPro.app",
    icon="resources/icons/vault.png",
    bundle_identifier=None,
)
'''
        spec_path.write_text(spec_content, encoding="utf-8")

    # Clean previous build artifacts
    dist_dir = PROJECT_ROOT / "dist"
    build_dir = PROJECT_ROOT / "build"
    if dist_dir.exists():
        shutil.rmtree(dist_dir, ignore_errors=True)
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)

    # Run PyInstaller
    cmd = [
        "pyinstaller",
        "--name",
        "SecureVaultPro",
        "--noconfirm",
        "--noconsole",
        "--icon",
        "resources/icons/vault.png",
        "--add-data",
        "resources;resources",
        "--add-data",
        "docs;docs",
        "main.py",
    ]
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("PyInstaller build failed")

    # Verify the onedir output exists
    if not DIST_DIR.exists():
        # PyInstaller may have created dist/SecureVaultPro.exe (onefile) instead
        # Look for the exe or the onedir folder
        exe_path = dist_dir / "SecureVaultPro.exe"
        if exe_path.exists():
            # Move onefile to onedir layout
            onedir_dir = dist_dir / "SecureVaultPro"
            onedir_dir.mkdir(parents=True, exist_ok=True)
            exe_path.rename(onedir_dir / "SecureVaultPro.exe")
        else:
            raise FileNotFoundError(
                f"Packaged app not found at {DIST_DIR}. PyInstaller build may have failed."
            )


def _build_zip(zip_path: Path) -> None:
    """Zip the contents of dist/SecureVaultPro into zip_path at the zip root."""
    if not DIST_DIR.exists():
        raise FileNotFoundError(
            f"Dist directory not found: {DIST_DIR}. Build the app first."
        )
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(DIST_DIR.rglob("*")):
            arcname = file_path.relative_to(DIST_DIR)
            zf.write(file_path, arcname)


def build_update(
    url: str | None = None,
    notes: str | None = None,
    skip_build: bool = False,
) -> dict:
    """Build the release ZIP and manifest.

    Args:
        url: Manifest URL override. Preserves existing value if omitted.
        notes: Release notes override. Preserves existing value if omitted.
        skip_build: If True, do not rebuild the ZIP or package the app
            (re-use existing release ZIP).

    Returns:
        The manifest dict that was written to disk.
    """
    existing = _load_existing_manifest()
    version_str = existing.get("version", APP_VERSION)
    if not version_str:
        version_str = APP_VERSION

    zip_name = f"SecureVaultPro_{version_str}.zip"
    zip_path = RELEASES_DIR / zip_name

    if not skip_build:
        # Step 1: Package the app with PyInstaller
        _package_app()
        # Step 2: Build the release ZIP from the packaged output
        _build_zip(zip_path)
    elif not zip_path.exists():
        raise FileNotFoundError(
            f"No existing release ZIP at {zip_path}; run without --skip-build first."
        )

    sha256 = _compute_sha256(zip_path)
    size_bytes = zip_path.stat().st_size
    published_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if url is None:
        url = existing.get("url", "")
    if notes is None:
        notes = existing.get("notes", "")

    manifest = {
        "version": version_str,
        "url": url,
        "sha256": sha256,
        "size_bytes": size_bytes,
        "notes": notes,
        "published_at": published_at,
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Built release ZIP: {zip_path}")
    print(f"SHA-256: {sha256}")
    print(f"Size: {size_bytes} bytes")
    print(f"Manifest written to: {MANIFEST_PATH}")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a SecureVault Pro release ZIP and update manifest."
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Re-use the existing release ZIP instead of rebuilding.",
    )
    parser.add_argument(
        "--url",
        help="Manifest URL (preserved across rebuilds if already set).",
    )
    parser.add_argument(
        "--notes",
        help="Release notes (preserved across rebuilds if already set).",
    )
    args = parser.parse_args()

    build_update(url=args.url, notes=args.notes, skip_build=args.skip_build)


if __name__ == "__main__":
    main()
