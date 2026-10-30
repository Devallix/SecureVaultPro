"""Tests for update version comparison."""

import pytest

from app.core.updates.version import Version, compare_versions, parse_version


class TestParseVersion:
    def test_basic_three_part(self) -> None:
        assert parse_version("0.1.0") == Version(0, 1, 0)

    def test_leading_v(self) -> None:
        assert parse_version("v0.1.0") == Version(0, 1, 0)

    def test_two_part(self) -> None:
        assert parse_version("1.2") == Version(1, 2, 0, 0)

    def test_one_part(self) -> None:
        assert parse_version("3") == Version(3, 0, 0, 0)

    def test_four_part(self) -> None:
        assert parse_version("1.2.3.4") == Version(1, 2, 3, 4)

    def test_invalid(self) -> None:
        with pytest.raises(ValueError):
            parse_version("not-a-version")
        with pytest.raises(ValueError):
            parse_version("1.2.3.4.5")
        with pytest.raises(ValueError):
            parse_version("")


class TestCompareVersions:
    def test_newer_than(self) -> None:
        assert compare_versions("0.1.1", "0.1.0") > 0
        assert compare_versions("0.1.10", "0.1.9") > 0
        assert compare_versions("0.2.0", "0.1.2") > 0
        assert compare_versions("1.0.0", "0.99.99") > 0

    def test_equal(self) -> None:
        assert compare_versions("0.1.0", "0.1.0") == 0
        assert compare_versions("v0.1.0", "0.1.0") == 0

    def test_older_than(self) -> None:
        assert compare_versions("0.1.0", "0.1.1") < 0
        assert compare_versions("0.1.9", "0.1.10") < 0

    def test_build_component(self) -> None:
        assert compare_versions("1.0.0.1", "1.0.0.0") > 0


class TestVersionDataclass:
    def test_str(self) -> None:
        assert str(Version(0, 1, 0)) == "0.1.0"
        assert str(Version(1, 0, 0)) == "1.0.0"
        assert str(Version(1, 2, 0, 0)) == "1.2.0"
        assert str(Version(1, 2, 3, 4)) == "1.2.3.4"

    def test_is_newer_than(self) -> None:
        assert Version(0, 1, 1).is_newer_than(Version(0, 1, 0))
        assert not Version(0, 1, 0).is_newer_than(Version(0, 1, 0))
        assert not Version(0, 1, 0).is_newer_than(Version(0, 1, 1))
