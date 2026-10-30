"""Update manifest parsing and validation.

The manifest is a JSON document published alongside the release ZIP that tells
the built-in updater about available updates.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.updates.version import Version, parse_version


class ManifestError(ValueError):
    """Raised when a manifest is invalid or missing required fields."""


@dataclass(frozen=True)
class Manifest:
    """A parsed update manifest.

    Attributes:
        version: The release version.
        url: HTTPS URL to the release ZIP.
        sha256: Optional SHA-256 hex digest of the ZIP for verification.
        size_bytes: Optional expected size of the ZIP in bytes.
        notes: Optional release notes.
        published_at: Optional ISO-8601 / human-readable publication timestamp.
    """

    version: Version
    url: str
    sha256: str | None = None
    size_bytes: int | None = None
    notes: str | None = None
    published_at: str | None = None

    @property
    def version_str(self) -> str:
        """The version as a string."""
        return str(self.version)

    def is_newer_than(self, current_version: str) -> bool:
        """Return True if this manifest's version is newer than ``current_version``."""
        try:
            current = parse_version(current_version)
        except ValueError:
            return False
        return self.version.is_newer_than(current)

    def to_dict(self) -> dict[str, Any]:
        """Serialise the manifest to a JSON-compatible dict."""
        data: dict[str, Any] = {
            "version": self.version_str,
            "url": self.url,
        }
        if self.sha256 is not None:
            data["sha256"] = self.sha256
        if self.size_bytes is not None:
            data["size_bytes"] = self.size_bytes
        if self.notes is not None:
            data["notes"] = self.notes
        if self.published_at is not None:
            data["published_at"] = self.published_at
        return data


def parse_manifest(data: dict[str, Any]) -> Manifest:
    """Parse and validate a manifest dict.

    Args:
        data: Raw manifest dictionary (already decoded from JSON).

    Returns:
        A validated :class:`Manifest`.

    Raises:
        ManifestError: If required fields are missing or invalid.
    """
    if not isinstance(data, dict):
        raise ManifestError("Manifest must be a JSON object")

    version_raw = data.get("version")
    if not version_raw or not isinstance(version_raw, str):
        raise ManifestError("Manifest missing required 'version' field")

    try:
        version = parse_version(version_raw)
    except ValueError as exc:
        raise ManifestError(f"Invalid manifest version: {exc}") from exc

    url = data.get("url")
    if not url or not isinstance(url, str):
        raise ManifestError("Manifest missing required 'url' field")

    sha256 = data.get("sha256")
    if sha256 is not None and not isinstance(sha256, str):
        raise ManifestError("Manifest 'sha256' must be a string")

    size_bytes = data.get("size_bytes")
    if size_bytes is not None and not isinstance(size_bytes, int):
        raise ManifestError("Manifest 'size_bytes' must be an integer")

    notes = data.get("notes")
    if notes is not None and not isinstance(notes, str):
        raise ManifestError("Manifest 'notes' must be a string")

    published_at = data.get("published_at")
    if published_at is not None and not isinstance(published_at, str):
        raise ManifestError("Manifest 'published_at' must be a string")

    return Manifest(
        version=version,
        url=url,
        sha256=sha256,
        size_bytes=size_bytes,
        notes=notes,
        published_at=published_at,
    )


def load_manifest_from_file(path: str | Path) -> Manifest:
    """Load a manifest from a JSON file on disk.

    Args:
        path: Path to the manifest JSON file.

    Returns:
        A validated :class:`Manifest`.

    Raises:
        ManifestError: If the file cannot be read or parsed.
    """
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"Failed to load manifest from {path}: {exc}") from exc
    return parse_manifest(data)


def manifest_to_json(manifest: Manifest, indent: int = 2) -> str:
    """Serialise a manifest to a JSON string."""
    return json.dumps(manifest.to_dict(), indent=indent, ensure_ascii=False)
