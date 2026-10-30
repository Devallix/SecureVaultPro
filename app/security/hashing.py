"""Hashing utilities: SHA-2, SHA-3, BLAKE2."""

import hashlib

from app.logging.logger import get_logger

logger = get_logger(__name__)


def hash_sha256(data: bytes) -> bytes:
    """Hash data with SHA-256.

    Args:
        data: Data to hash.

    Returns:
        32-byte hash digest.
    """
    return hashlib.sha256(data).digest()


def hash_sha384(data: bytes) -> bytes:
    """Hash data with SHA-384.

    Args:
        data: Data to hash.

    Returns:
        48-byte hash digest.
    """
    return hashlib.sha384(data).digest()


def hash_sha512(data: bytes) -> bytes:
    """Hash data with SHA-512.

    Args:
        data: Data to hash.

    Returns:
        64-byte hash digest.
    """
    return hashlib.sha512(data).digest()


def hash_sha3_256(data: bytes) -> bytes:
    """Hash data with SHA3-256.

    Args:
        data: Data to hash.

    Returns:
        32-byte hash digest.
    """
    return hashlib.sha3_256(data).digest()


def hash_blake2b(data: bytes, digest_size: int = 32) -> bytes:
    """Hash data with BLAKE2b.

    Args:
        data: Data to hash.
        digest_size: Output digest size in bytes.

    Returns:
        Hash digest.
    """
    return hashlib.blake2b(data, digest_size=digest_size).digest()


def hash_blake2s(data: bytes, digest_size: int = 32) -> bytes:
    """Hash data with BLAKE2s.

    Args:
        data: Data to hash.
        digest_size: Output digest size in bytes.

    Returns:
        Hash digest.
    """
    return hashlib.blake2s(data, digest_size=digest_size).digest()


def compute_file_checksum(file_path: str, algorithm: str = "sha256") -> str:
    """Compute a file checksum using the specified algorithm.

    Args:
        file_path: Path to the file.
        algorithm: Hash algorithm name.

    Returns:
        Hex-encoded checksum string.
    """
    h = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
