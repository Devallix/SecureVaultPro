"""HMAC-based integrity verification utilities."""

import hashlib
import hmac

from app.core.exceptions import IntegrityCheckError
from app.logging.logger import get_logger

logger = get_logger(__name__)


def compute_hmac(key: bytes, data: bytes, algorithm: str = "sha256") -> bytes:
    """Compute an HMAC of the given data.

    Args:
        key: HMAC key.
        data: Data to authenticate.
        algorithm: Hash algorithm for the HMAC.

    Returns:
        HMAC tag bytes.
    """
    return hmac.new(key, data, getattr(hashlib, algorithm)).digest()


def verify_hmac(key: bytes, data: bytes, expected_tag: bytes, algorithm: str = "sha256") -> bool:
    """Verify an HMAC tag using constant-time comparison.

    Args:
        key: HMAC key.
        data: Data that was authenticated.
        expected_tag: The HMAC tag to verify against.
        algorithm: Hash algorithm for the HMAC.

    Returns:
        True if the HMAC is valid.

    Raises:
        IntegrityCheckError: If integrity check fails.
    """
    computed = compute_hmac(key, data, algorithm)
    if not hmac.compare_digest(computed, expected_tag):
        logger.warning("HMAC integrity check failed")
        raise IntegrityCheckError("Data integrity check failed - data may be corrupted or tampered")
    return True


def compute_checksum(data: bytes, algorithm: str = "sha256") -> str:
    """Compute a hex-encoded checksum.

    Args:
        data: Data to checksum.
        algorithm: Hash algorithm.

    Returns:
        Hex string.
    """
    h = hashlib.new(algorithm)
    h.update(data)
    return h.hexdigest()
