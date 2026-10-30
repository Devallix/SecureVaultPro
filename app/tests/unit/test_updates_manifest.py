"""Tests for update manifest parsing and validation."""

import json
import tempfile
from pathlib import Path

import pytest

from app.core.updates.manifest import (
    ManifestError,
    load_manifest_from_file,
    manifest_to_json,
    parse_manifest,
)

VALID_MANIFEST = {
    "version": "0.1.1",
    "url": "https://example.com/SecureVaultPro_0.1.1.zip",
    "sha256": "85050B8B79E81DF953DEA3C90794C4418C03EE634A366AD498DF8901367BEE58",
    "size_bytes": 80792385,
    "notes": "Scan Folder quick action; updater fixes",
    "published_at": "2026-08-08 15:30:51",
}


class TestParseManifest:
    def test_valid_manifest(self) -> None:
        manifest = parse_manifest(VALID_MANIFEST)
        assert manifest.version_str == "0.1.1"
        assert manifest.url == VALID_MANIFEST["url"]
        assert manifest.sha256 == VALID_MANIFEST["sha256"]
        assert manifest.size_bytes == VALID_MANIFEST["size_bytes"]
        assert manifest.notes == VALID_MANIFEST["notes"]
        assert manifest.published_at == VALID_MANIFEST["published_at"]

    def test_minimal_manifest(self) -> None:
        manifest = parse_manifest(
            {"version": "1.0.0", "url": "https://example.com/app.zip"}
        )
        assert manifest.version_str == "1.0.0"
        assert manifest.sha256 is None
        assert manifest.size_bytes is None
        assert manifest.notes is None
        assert manifest.published_at is None

    def test_missing_version(self) -> None:
        with pytest.raises(ManifestError):
            parse_manifest({"url": "https://example.com/app.zip"})

    def test_missing_url(self) -> None:
        with pytest.raises(ManifestError):
            parse_manifest({"version": "1.0.0"})

    def test_invalid_version(self) -> None:
        with pytest.raises(ManifestError):
            parse_manifest({"version": "not-a-version", "url": "https://example.com/app.zip"})

    def test_not_a_dict(self) -> None:
        with pytest.raises(ManifestError):
            parse_manifest("not a dict")  # type: ignore[arg-type]

    def test_invalid_sha256_type(self) -> None:
        with pytest.raises(ManifestError):
            parse_manifest(
                {"version": "1.0.0", "url": "https://example.com/app.zip", "sha256": 123}
            )


class TestManifestIsNewerThan:
    def test_newer(self) -> None:
        manifest = parse_manifest(VALID_MANIFEST)
        assert manifest.is_newer_than("0.1.0")
        assert not manifest.is_newer_than("0.1.9")

    def test_not_newer(self) -> None:
        manifest = parse_manifest(VALID_MANIFEST)
        assert not manifest.is_newer_than("0.1.1")
        assert not manifest.is_newer_than("0.2.0")
        assert not manifest.is_newer_than("1.0.0")

    def test_invalid_current_version(self) -> None:
        manifest = parse_manifest(VALID_MANIFEST)
        assert not manifest.is_newer_than("not-a-version")


class TestManifestToJson:
    def test_round_trip(self) -> None:
        manifest = parse_manifest(VALID_MANIFEST)
        data = json.loads(manifest_to_json(manifest))
        assert data["version"] == "0.1.1"
        assert data["url"] == VALID_MANIFEST["url"]
        assert data["sha256"] == VALID_MANIFEST["sha256"]


class TestLoadManifestFromFile:
    def test_load_from_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text(json.dumps(VALID_MANIFEST), encoding="utf-8")
            manifest = load_manifest_from_file(path)
            assert manifest.version_str == "0.1.1"

    def test_missing_file(self) -> None:
        with pytest.raises(ManifestError):
            load_manifest_from_file("/nonexistent/manifest.json")

    def test_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text("{not valid json", encoding="utf-8")
            with pytest.raises(ManifestError):
                load_manifest_from_file(path)
