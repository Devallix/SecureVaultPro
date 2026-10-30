"""Key derivation functions for SecureVault Pro.

Implements Argon2id (primary), scrypt, HKDF, and PBKDF2 (legacy).
"""

import hmac

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id as _Argon2id
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from app.core.constants import (
    ARGON2_HASH_LEN,
    ARGON2_MEMORY_COST,
    ARGON2_PARALLELISM,
    ARGON2_TIME_COST,
    SCRYPT_N,
    SCRYPT_P,
    SCRYPT_R,
)
from app.core.exceptions import KDFError
from app.logging.logger import get_logger

logger = get_logger(__name__)


def derive_key_argon2id(
    password: bytes,
    salt: bytes,
    time_cost: int = ARGON2_TIME_COST,
    memory_cost: int = ARGON2_MEMORY_COST,
    parallelism: int = ARGON2_PARALLELISM,
    hash_len: int = ARGON2_HASH_LEN,
) -> bytes:
    """Derive a key using Argon2id (recommended primary KDF).

    Args:
        password: The password bytes.
        salt: The salt bytes.
        time_cost: Number of iterations.
        memory_cost: Memory usage in KiB.
        parallelism: Degree of parallelism.
        hash_len: Length of the derived key.

    Returns:
        Derived key bytes.

    Raises:
        KDFError: If key derivation fails.
    """
    try:
        kdf = _Argon2id(
            salt=salt,
            length=hash_len,
            iterations=time_cost,
            lanes=parallelism,
            memory_cost=memory_cost,
        )
        key = kdf.derive(password)
        logger.debug("Argon2id key derived (len={length})", length=len(key))
        return key
    except Exception as e:
        raise KDFError(f"Argon2id key derivation failed: {e}") from e


def derive_key_scrypt(
    password: bytes,
    salt: bytes,
    n: int = SCRYPT_N,
    r: int = SCRYPT_R,
    p: int = SCRYPT_P,
    key_len: int = 32,
) -> bytes:
    """Derive a key using scrypt.

    Args:
        password: The password bytes.
        salt: The salt bytes.
        n: CPU/memory cost parameter.
        r: Block size parameter.
        p: Parallelization parameter.
        key_len: Length of the derived key.

    Returns:
        Derived key bytes.

    Raises:
        KDFError: If key derivation fails.
    """
    try:
        kdf = Scrypt(salt=salt, length=key_len, n=n, r=r, p=p)
        key = kdf.derive(password)
        logger.debug("scrypt key derived (len={length})", length=len(key))
        return key
    except Exception as e:
        raise KDFError(f"scrypt key derivation failed: {e}") from e


def derive_key_hkdf(
    key_material: bytes,
    salt: bytes,
    info: bytes,
    length: int = 32,
) -> bytes:
    """Derive a key using HKDF-SHA256.

    Args:
        key_material: The input key material.
        salt: The salt.
        info: Context/application-specific info.
        length: Output key length.

    Returns:
        Derived key bytes.

    Raises:
        KDFError: If key derivation fails.
    """
    try:
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            info=info,
        )
        return hkdf.derive(key_material)
    except Exception as e:
        raise KDFError(f"HKDF key derivation failed: {e}") from e


def derive_key_pbkdf2(
    password: bytes,
    salt: bytes,
    iterations: int = 600_000,
    length: int = 32,
) -> bytes:
    """Derive a key using PBKDF2-HMAC-SHA256 (legacy compatibility).

    Args:
        password: The password bytes.
        salt: The salt bytes.
        iterations: Number of iterations.
        length: Output key length.

    Returns:
        Derived key bytes.

    Raises:
        KDFError: If key derivation fails.
    """
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            iterations=iterations,
        )
        return kdf.derive(password)
    except Exception as e:
        raise KDFError(f"PBKDF2 key derivation failed: {e}") from e


def verify_password_argon2id(password: bytes, salt: bytes, expected_hash: bytes) -> bool:
    """Verify a password against an Argon2id hash.

    Args:
        password: The password to verify.
        salt: The salt used during hashing.
        expected_hash: The expected hash to compare against.

    Returns:
        True if the password matches.
    """
    try:
        derived = derive_key_argon2id(password, salt, hash_len=len(expected_hash))
        return hmac.compare_digest(derived, expected_hash)
    except KDFError:
        return False
