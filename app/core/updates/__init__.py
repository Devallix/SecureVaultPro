"""SecureVault Pro update service package.

Provides the built-in updater pipeline: manifest checking, background download,
SHA-256 verification, and the install/swap batch script generation.
"""

from app.core.updates.manifest import Manifest, ManifestError
from app.core.updates.swap import SwapBatch, generate_swap_batch
from app.core.updates.updater import UpdateService
from app.core.updates.version import Version, compare_versions, parse_version

__all__ = [
    "UpdateService",
    "Manifest",
    "ManifestError",
    "Version",
    "compare_versions",
    "parse_version",
    "generate_swap_batch",
    "SwapBatch",
]
