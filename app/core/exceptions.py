"""Custom exception hierarchy for SecureVault Pro.

All application exceptions inherit from SecureVaultError to enable
centralised error handling and logging.
"""


class SecureVaultError(Exception):
    """Base exception for all SecureVault errors."""

    def __init__(self, message: str = "An unexpected error occurred") -> None:
        self.message = message
        super().__init__(self.message)


# --- Authentication ---


class AuthenticationError(SecureVaultError):
    """Raised when authentication fails."""


class MasterPasswordError(AuthenticationError):
    """Raised when master password verification fails."""


class InvalidMasterPasswordError(MasterPasswordError):
    """Raised when the supplied master password is incorrect."""


class MasterPasswordChangeError(AuthenticationError):
    """Raised when master password change fails."""


class RecoveryKeyError(AuthenticationError):
    """Raised when recovery key verification fails."""


class MaxAttemptsExceededError(AuthenticationError):
    """Raised when too many authentication attempts are made."""

    def __init__(self, max_attempts: int = 5) -> None:
        self.max_attempts = max_attempts
        super().__init__(f"Maximum authentication attempts ({max_attempts}) exceeded")


# --- Vault ---


class VaultError(SecureVaultError):
    """Raised when a vault operation fails."""


class VaultNotFoundError(VaultError):
    """Raised when a vault cannot be found."""

    def __init__(self, vault_id: str = "") -> None:
        self.vault_id = vault_id
        super().__init__(f"Vault not found: {vault_id}" if vault_id else "Vault not found")


class VaultLockError(VaultError):
    """Raised when vault lock operation fails."""


class VaultUnlockError(VaultError):
    """Raised when vault unlock operation fails."""


class VaultCorruptionError(VaultError):
    """Raised when vault integrity check fails."""


# --- Encryption ---


class CryptoError(SecureVaultError):
    """Raised when a cryptographic operation fails."""


class EncryptionError(CryptoError):
    """Raised when encryption fails."""


class DecryptionError(CryptoError):
    """Raised when decryption fails."""


class IntegrityCheckError(CryptoError):
    """Raised when integrity verification fails."""


class KDFError(CryptoError):
    """Raised when key derivation fails."""


class UnsupportedAlgorithmError(CryptoError):
    """Raised when an unsupported algorithm is requested."""


# --- Database ---


class DatabaseError(SecureVaultError):
    """Raised when a database operation fails."""


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""


class DatabaseMigrationError(DatabaseError):
    """Raised when a database migration fails."""


# --- File Operations ---


class FileOperationError(SecureVaultError):
    """Raised when a file operation fails."""


class VaultFileNotFoundError(FileOperationError):
    """Raised when a required file is not found."""


class FileTooLargeError(FileOperationError):
    """Raised when a file exceeds the maximum size limit."""


class SecureDeleteError(FileOperationError):
    """Raised when secure file deletion fails."""


# --- Backup ---


class BackupError(SecureVaultError):
    """Raised when a backup operation fails."""


class RestoreError(BackupError):
    """Raised when a restore operation fails."""


class BackupIntegrityError(BackupError):
    """Raised when backup integrity check fails."""


# --- Import/Export ---


class DataImportError(SecureVaultError):
    """Raised when data import fails."""


class ExportError(SecureVaultError):
    """Raised when data export fails."""


class InvalidFileFormatError(DataImportError):
    """Raised when an imported file has an invalid format."""


class ImportValidationError(DataImportError):
    """Raised when imported data fails validation."""


# --- Configuration ---


class ConfigurationError(SecureVaultError):
    """Raised when configuration is invalid or missing."""


# --- Plugin ---


class PluginError(SecureVaultError):
    """Raised when a plugin operation fails."""


class PluginLoadError(PluginError):
    """Raised when a plugin fails to load."""


# --- Workers ---


class WorkerError(SecureVaultError):
    """Raised when a background worker fails."""
