"""SecureVault Pro update service.

Orchestrates the update pipeline: checking for updates against a manifest
endpoint, downloading the release ZIP, verifying its SHA-256 digest, and
generating the install/swap batch script.
"""

from __future__ import annotations

import hashlib
import urllib.request
from collections.abc import Callable
from pathlib import Path

from app.core.config import AppConfig
from app.core.updates.manifest import Manifest, ManifestError
from app.core.updates.swap import generate_swap_batch
from app.logging.logger import get_logger

logger = get_logger(__name__)

CHUNK_SIZE = 64 * 1024


class UpdateService:
    """Service for checking, downloading, and installing application updates.

    The service is intentionally free of Qt dependencies so it can be unit
    tested without a QApplication. UI signalling is handled by
    :class:`app.workers.update_worker.UpdateWorker`.
    """

    DEFAULT_ENDPOINT = (
        "https://github.com/Devallix/SecureVaultPro/"
        "raw/refs/heads/main/manifest.json"
    )

    def __init__(
        self,
        config: AppConfig | None = None,
        current_version: str = "0.1.0",
    ) -> None:
        self._config = config or AppConfig()
        self._current_version = current_version
        self._logger = logger

    @property
    def current_version(self) -> str:
        """The running application version."""
        return self._current_version

    @property
    def endpoint(self) -> str:
        """The configured update manifest endpoint."""
        return str(self._config.get("updates.endpoint", self.DEFAULT_ENDPOINT))

    @endpoint.setter
    def endpoint(self, value: str) -> None:
        self._config.set("updates.endpoint", value)

    @property
    def check_enabled(self) -> bool:
        """Whether automatic update checks are enabled."""
        return bool(self._config.get("updates.check_enabled", True))

    @check_enabled.setter
    def check_enabled(self, value: bool) -> None:
        self._config.set("updates.check_enabled", value)

    def check_for_updates(
        self,
        endpoint: str | None = None,
        current_version: str | None = None,
    ) -> Manifest | None:
        """Fetch the manifest and return it if an update is available.

        Args:
            endpoint: Override the configured endpoint URL.
            current_version: Override the running version for comparison.

        Returns:
            A :class:`Manifest` if a newer version is available, else ``None``.

        Raises:
            ManifestError: If the manifest is invalid.
            URLError / HTTPError: If the endpoint cannot be reached.
        """
        url = endpoint or self.endpoint
        version = current_version or self._current_version

        self._logger.info("Checking for updates at {url}", url=url)

        with urllib.request.urlopen(url, timeout=15) as response:
            if response.status != 200:
                raise ManifestError(
                    f"Manifest endpoint returned HTTP {response.status}"
                )
            raw = response.read()

        try:
            import json

            data = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ManifestError(f"Manifest is not valid JSON: {exc}") from exc

        from app.core.updates.manifest import parse_manifest

        manifest = parse_manifest(data)

        if manifest.is_newer_than(version):
            self._logger.info(
                "Update available: {current} -> {new}",
                current=version,
                new=manifest.version_str,
            )
            return manifest

        self._logger.info(
            "No update available (running {current}, manifest {new})",
            current=version,
            new=manifest.version_str,
        )
        return None

    def download_update(
        self,
        manifest: Manifest,
        progress_callback: Callable[[int], None] | None = None,
    ) -> str:
        """Download the release ZIP to the app temp directory.

        Args:
            manifest: The manifest describing the update.
            progress_callback: Optional callback receiving bytes downloaded so far.

        Returns:
            Absolute path to the downloaded ZIP file.

        Raises:
            URLError / HTTPError: If the download fails.
            ValueError: If the server does not send Content-Length and
                progress reporting is required.
        """
        url = manifest.url

        temp_dir = Path(self._config.temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        dest = temp_dir / f"SecureVaultPro_{manifest.version_str}.zip"

        self._logger.info("Downloading update from {url} to {dest}", url=url, dest=dest)

        downloaded = 0
        with urllib.request.urlopen(url, timeout=30) as response:
            if response.status != 200:
                raise ManifestError(
                    f"Download endpoint returned HTTP {response.status}"
                )
            content_length = response.headers.get("Content-Length")
            expected_total = int(content_length) if content_length else None

            with open(dest, "wb") as out_file:
                while True:
                    chunk = response.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and expected_total:
                        progress_callback(int(downloaded / expected_total * 100))

        if expected_total is not None and downloaded != expected_total:
            dest.unlink(missing_ok=True)
            raise ManifestError(
                f"Download incomplete: {downloaded} of {expected_total} bytes"
            )

        self._logger.info("Download complete: {dest} ({downloaded} bytes)", dest=dest, downloaded=downloaded)
        return str(dest)

    def verify_sha256(self, file_path: str, expected_sha256: str) -> bool:
        """Verify the SHA-256 digest of a file.

        Args:
            file_path: Path to the file to verify.
            expected_sha256: Expected lowercase hex digest.

        Returns:
            True if the digest matches.
        """
        actual = self._compute_sha256(file_path)
        match = actual.lower() == expected_sha256.lower()
        self._logger.debug(
            "SHA-256 verification {result}: expected={expected}, actual={actual}",
            result="passed" if match else "failed",
            expected=expected_sha256,
            actual=actual,
        )
        return match

    def _compute_sha256(self, file_path: str) -> str:
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                h.update(chunk)
        return h.hexdigest()

    def prepare_install(
        self,
        zip_path: str,
        install_dir: str | Path | None = None,
        expected_sha256: str | None = None,
    ) -> str:
        """Verify and prepare the update for installation.

        Validates the SHA-256 digest (if expected) and generates the swap
        batch script. Does not quit the app or run the batch itself.

        Args:
            zip_path: Path to the downloaded update ZIP.
            install_dir: Override the install directory. Defaults to the
                directory containing this package's runtime entry point.
            expected_sha256: Expected SHA-256 digest of the ZIP.

        Returns:
            The path to the generated swap batch file.

        Raises:
            ManifestError: If SHA-256 verification fails.
        """
        if expected_sha256 and not self.verify_sha256(zip_path, expected_sha256):
            raise ManifestError("SHA-256 verification failed for update ZIP")

        if install_dir is None:
            install_dir = Path(__file__).resolve().parents[3]

        bat_dir = Path(self._config.temp_dir)
        bat_dir.mkdir(parents=True, exist_ok=True)
        bat_path = bat_dir / "SecureVaultPro_updater.bat"

        batch = generate_swap_batch(
            install_dir=install_dir,
            zip_path=zip_path,
            bat_path=bat_path,
        )
        batch.write()

        self._logger.info("Swap batch written to {bat_path}", bat_path=bat_path)
        return str(bat_path)



