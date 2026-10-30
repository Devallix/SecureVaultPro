"""Recovery key service for vault recovery."""

import base64

from app.core.exceptions import InvalidMasterPasswordError
from app.logging.logger import get_logger
from app.models.recovery_key import RecoveryKey
from app.repositories.recovery_key_repository import RecoveryKeyRepository
from app.security.kdf import derive_key_argon2id
from app.security.secure_random import generate_nonce, generate_recovery_words
from app.security.symmetric import decrypt_chacha20, encrypt_chacha20

logger = get_logger(__name__)


class RecoveryKeyService:
    """Service for generating, storing, and verifying recovery keys."""

    def __init__(self, repo: RecoveryKeyRepository) -> None:
        self._repo = repo

    def generate_and_store(
        self, vault_id: str, vault_salt_hex: str, vault_key: bytes
    ) -> list[str]:
        """Generate a 12-word recovery key and store its hash plus the encrypted vault key.

        The vault encryption key is encrypted with a key derived from the
        recovery passphrase, so that providing the correct recovery passphrase
        at recovery time yields the original vault key used to encrypt all data.

        Args:
            vault_id: The vault identifier.
            vault_salt_hex: Hex-encoded vault salt.
            vault_key: The 32-byte vault encryption key to protect.

        Returns:
            The 12-word recovery passphrase.
        """
        words = generate_recovery_words(12)
        passphrase = " ".join(words)

        vault_salt = bytes.fromhex(vault_salt_hex)
        recovery_key = derive_key_argon2id(
            passphrase.encode("utf-8"), vault_salt, hash_len=32
        )
        key_hash = recovery_key.hex()

        nonce = generate_nonce(12)
        encrypted = encrypt_chacha20(recovery_key, vault_key, nonce)
        encrypted_b64 = base64.b64encode(nonce + encrypted).decode("ascii")

        recovery = RecoveryKey(
            vault_id=vault_id,
            key_hash=key_hash,
            encrypted_vault_key=encrypted_b64,
            is_used=False,
        )
        self._repo.create(recovery)

        logger.info("Recovery key generated and stored for vault: {vault}", vault=vault_id)
        return words

    def verify_and_unlock(self, words: list[str], vault_id: str, vault_salt_hex: str) -> bytes:
        """Verify a recovery key passphrase and return the vault key.

        Verification is done against the stored RecoveryKey.key_hash. On success,
        the original vault encryption key (protected by the recovery passphrase)
        is decrypted and returned.

        Args:
            words: The 12 recovery words.
            vault_id: The vault identifier.
            vault_salt_hex: Hex-encoded vault salt.

        Returns:
            The 32-byte vault encryption key.

        Raises:
            InvalidMasterPasswordError: If verification fails or no key exists.
        """
        if len(words) != 12:
            raise InvalidMasterPasswordError("Recovery key must be exactly 12 words")

        passphrase = " ".join(words)
        vault_salt = bytes.fromhex(vault_salt_hex)

        recovery = self._repo.get_active_by_vault(vault_id)
        if recovery is None:
            raise InvalidMasterPasswordError("No active recovery key found for this vault.")

        from app.authentication.recovery_key import verify_recovery_key

        if not verify_recovery_key(passphrase, vault_salt_hex, recovery.key_hash):
            raise InvalidMasterPasswordError("Incorrect recovery key.")

        if recovery.encrypted_vault_key is None:
            raise InvalidMasterPasswordError("No protected vault key stored for recovery.")

        payload = base64.b64decode(recovery.encrypted_vault_key)
        nonce = payload[:12]
        ciphertext = payload[12:]

        recovery_key = derive_key_argon2id(
            passphrase.encode("utf-8"), vault_salt, hash_len=32
        )
        return decrypt_chacha20(recovery_key, ciphertext, nonce)
