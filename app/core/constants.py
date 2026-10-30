"""Application-wide constants for SecureVault Pro."""

from typing import Final

APP_NAME: Final[str] = "SecureVault Pro"
APP_VERSION: Final[str] = "0.1.0"
APP_TAGLINE: Final[str] = "Protect Everything. Trust Nothing."
APP_DESCRIPTION: Final[str] = "Enterprise-grade file encryption and password management."

# --- Directories ---
APP_DIR_NAME: Final[str] = ".securevault"
DATA_DIR_NAME: Final[str] = "data"
LOGS_DIR_NAME: Final[str] = "logs"
BACKUPS_DIR_NAME: Final[str] = "backups"
TEMP_DIR_NAME: Final[str] = "temp"

# --- Database ---
DATABASE_NAME: Final[str] = "vault.db"

# --- Security ---
ARGON2_TIME_COST: Final[int] = 3
ARGON2_MEMORY_COST: Final[int] = 65536
ARGON2_PARALLELISM: Final[int] = 4
ARGON2_HASH_LEN: Final[int] = 32
ARGON2_SALT_LEN: Final[int] = 16

SCRYPT_N: Final[int] = 2**14
SCRYPT_R: Final[int] = 8
SCRYPT_P: Final[int] = 1

# --- Clipboard ---
CLIPBOARD_CLEAR_SECONDS: Final[int] = 30

# --- Auto-lock ---
AUTO_LOCK_TIMEOUT_SECONDS: Final[int] = 300

# --- Backup ---
MAX_BACKUP_VERSIONS: Final[int] = 10

# --- Audit ---
AUDIT_RETENTION_DAYS: Final[int] = 365

# --- UI ---
WINDOW_MIN_WIDTH: Final[int] = 1200
WINDOW_MIN_HEIGHT: Final[int] = 800
SPLASH_DURATION_MS: Final[int] = 4000

# --- Crypto algorithm versions ---
CRYPTO_VERSION_1_AES_GCM: Final[int] = 1
CRYPTO_VERSION_2_CHACHA20: Final[int] = 2
CURRENT_CRYPTO_VERSION: Final[int] = CRYPTO_VERSION_2_CHACHA20

# --- File encryption ---
FILE_CHUNK_SIZE: Final[int] = 64 * 1024
MAX_FILE_SIZE_MB: Final[int] = 2048

# --- Password generator ---
DEFAULT_PASSWORD_LENGTH: Final[int] = 20
MIN_PASSWORD_LENGTH: Final[int] = 8
MAX_PASSWORD_LENGTH: Final[int] = 128

# --- Recovery key ---
RECOVERY_KEY_WORDS: Final[int] = 12
