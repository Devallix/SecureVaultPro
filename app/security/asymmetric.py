"""Asymmetric encryption: RSA-4096, Ed25519, X25519."""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa, x25519
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP

from app.core.exceptions import CryptoError, EncryptionError
from app.logging.logger import get_logger

logger = get_logger(__name__)


def generate_rsa_keypair(key_size: int = 4096, password: bytes | None = None) -> tuple[bytes, bytes]:
    """Generate an RSA key pair.

    Args:
        key_size: Key size in bits (default 4096).
        password: Optional password to encrypt the private key.

    Returns:
        Tuple of (private_key_pem, public_key_pem).
    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    enc = serialization.BestAvailableEncryption(password) if password else serialization.NoEncryption()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc,
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    logger.debug("RSA-{key_size} keypair generated", key_size=key_size)
    return private_pem, public_pem


def generate_ed25519_keypair(password: bytes | None = None) -> tuple[bytes, bytes]:
    """Generate an Ed25519 signing key pair.

    Args:
        password: Optional password to encrypt the private key.

    Returns:
        Tuple of (private_key_pem, public_key_pem).
    """
    private_key = ed25519.Ed25519PrivateKey.generate()
    enc = serialization.BestAvailableEncryption(password) if password else serialization.NoEncryption()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc,
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    logger.debug("Ed25519 keypair generated")
    return private_pem, public_pem


def generate_x25519_keypair(password: bytes | None = None) -> tuple[bytes, bytes]:
    """Generate an X25519 key exchange pair.

    Args:
        password: Optional password to encrypt the private key.

    Returns:
        Tuple of (private_key_pem, public_key_pem).
    """
    private_key = x25519.X25519PrivateKey.generate()
    enc = serialization.BestAvailableEncryption(password) if password else serialization.NoEncryption()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc,
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    logger.debug("X25519 keypair generated")
    return private_pem, public_pem


def rsa_encrypt(public_key_pem: bytes, plaintext: bytes) -> bytes:
    """Encrypt data with an RSA public key (OAEP padding).

    Args:
        public_key_pem: PEM-encoded public key.
        plaintext: Data to encrypt.

    Returns:
        Encrypted bytes.

    Raises:
        EncryptionError: If encryption fails.
    """
    try:
        public_key = serialization.load_pem_public_key(public_key_pem)
        ciphertext = public_key.encrypt(
            plaintext,
            OAEP(
                mgf=MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return ciphertext
    except Exception as e:
        raise EncryptionError(f"RSA encryption failed: {e}") from e


def rsa_decrypt(private_key_pem: bytes, ciphertext: bytes) -> bytes:
    """Decrypt data with an RSA private key.

    Args:
        private_key_pem: PEM-encoded private key.
        ciphertext: Encrypted data.

    Returns:
        Decrypted plaintext bytes.

    Raises:
        CryptoError: If decryption fails.
    """
    from app.core.exceptions import DecryptionError

    try:
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        plaintext = private_key.decrypt(
            ciphertext,
            OAEP(
                mgf=MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return plaintext
    except Exception as e:
        raise DecryptionError(f"RSA decryption failed: {e}") from e


def ed25519_sign(private_key_pem: bytes, message: bytes) -> bytes:
    """Sign a message with an Ed25519 private key.

    Args:
        private_key_pem: PEM-encoded private key.
        message: Message to sign.

    Returns:
        Digital signature bytes.
    """
    try:
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        return private_key.sign(message)
    except Exception as e:
        raise CryptoError(f"Ed25519 signing failed: {e}") from e


def ed25519_verify(public_key_pem: bytes, message: bytes, signature: bytes) -> bool:
    """Verify an Ed25519 signature.

    Args:
        public_key_pem: PEM-encoded public key.
        message: Original message.
        signature: Signature to verify.

    Returns:
        True if the signature is valid.
    """
    try:
        public_key = serialization.load_pem_public_key(public_key_pem)
        public_key.verify(signature, message)
        return True
    except Exception:
        return False
