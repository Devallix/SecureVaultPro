"""Version parsing and numerical comparison for SecureVault Pro updates.

Handles semantic version strings with an optional leading ``v`` prefix and
compares them component-wise as integers so that ``0.1.10 > 0.1.9``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_VERSION_RE = re.compile(r"^v?(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:\.(\d+))?$")


@dataclass(frozen=True)
class Version:
    """A parsed application version.

    Components default to 0 when omitted. Comparison is lexicographic over the
    integer tuple ``(major, minor, patch, build)``.
    """

    major: int = 0
    minor: int = 0
    patch: int = 0
    build: int = 0

    def __str__(self) -> str:
        parts = [str(self.major), str(self.minor), str(self.patch)]
        if self.build != 0:
            parts.append(str(self.build))
        return ".".join(parts)

    def __lt__(self, other: Version) -> bool:
        return self._tuple() < other._tuple()

    def __le__(self, other: Version) -> bool:
        return self._tuple() <= other._tuple()

    def __gt__(self, other: Version) -> bool:
        return self._tuple() > other._tuple()

    def __ge__(self, other: Version) -> bool:
        return self._tuple() >= other._tuple()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self._tuple() == other._tuple()

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self._tuple() != other._tuple()

    def _tuple(self) -> tuple[int, int, int, int]:
        return (self.major, self.minor, self.patch, self.build)

    def is_newer_than(self, other: Version) -> bool:
        """Return True if this version is strictly newer than ``other``."""
        return self > other


def parse_version(value: str) -> Version:
    """Parse a version string into a :class:`Version`.

    Accepts an optional leading ``v`` and up to four dot-separated numeric
    components. Missing components default to 0.

    Args:
        value: Version string such as ``"0.1.1"`` or ``"v0.2.0"``.

    Returns:
        A :class:`Version` instance.

    Raises:
        ValueError: If ``value`` is not a valid version string.
    """
    match = _VERSION_RE.match(value.strip())
    if not match:
        raise ValueError(f"Invalid version string: {value!r}")
    return Version(
        major=int(match.group(1)),
        minor=int(match.group(2) or 0),
        patch=int(match.group(3) or 0),
        build=int(match.group(4) or 0),
    )


def compare_versions(a: str, b: str) -> int:
    """Compare two version strings numerically.

    Args:
        a: First version string.
        b: Second version string.

    Returns:
        Negative if ``a < b``, zero if equal, positive if ``a > b``.
    """
    va = parse_version(a)
    vb = parse_version(b)
    if va < vb:
        return -1
    if va > vb:
        return 1
    return 0
