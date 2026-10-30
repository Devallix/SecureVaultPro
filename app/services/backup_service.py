"""Backup service for SecureVault Pro."""

import hashlib
import shutil
from datetime import datetime
from pathlib import Path

from app.core.constants import MAX_BACKUP_VERSIONS
from app.logging.logger import get_logger
from app.security.crypto_engine import CryptoEngine

logger = get_logger(__name__)


class BackupService:
    """Service for creating, restoring, and managing encrypted vault backups."""

    def __init__(self, vault_key: bytes, vault_id: str, db_path: str, backup_dir: str) -> None:
        self._key = vault_key
        self._vault_id = vault_id
        self._db_path = db_path
        self._backup_dir = Path(backup_dir)
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        self._crypto = CryptoEngine()

    def _get_db_base(self) -> Path:
        """Return the base path of the database (without extension)."""
        return Path(self._db_path).with_suffix("")

    def create_backup(self) -> dict:
        """Create an encrypted backup of the vault database.

        Checkpoints the WAL so all data is in the main .db file,
        then encrypts and stores the backup.

        Returns:
            Dict with backup metadata.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{self._vault_id[:8]}_{timestamp}.db.bak"
        backup_path = self._backup_dir / backup_filename

        db_path = Path(self._db_path)
        if not db_path.exists():
            raise FileNotFoundError(f"Database not found: {self._db_path}")

        try:
            from sqlalchemy import text
            from app.database.session_factory import get_session
            with get_session() as session:
                session.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
        except Exception as e:
            logger.warning("WAL checkpoint failed, proceeding with raw copy: {err}", err=e)

        raw_data = db_path.read_bytes()
        encrypted = self._crypto.encrypt_bytes(self._key, raw_data)
        backup_path.write_bytes(encrypted.encode("utf-8"))

        checksum = hashlib.sha256(backup_path.read_bytes()).hexdigest()
        file_size = backup_path.stat().st_size

        self._cleanup_old_backups()

        logger.info("Encrypted backup created: {name} ({size} bytes)", name=backup_filename, size=file_size)
        return {
            "filename": backup_filename,
            "path": str(backup_path),
            "size": file_size,
            "checksum": checksum,
            "created_at": datetime.now().isoformat(),
        }

    def restore_backup(self, backup_path: str) -> bool:
        """Restore a vault from an encrypted backup file.

        Removes any WAL/SHM sidecar files, then writes the decrypted
        backup data as the main database file.

        Args:
            backup_path: Path to the backup file.

        Returns:
            True if successful.
        """
        source = Path(backup_path)
        if not source.exists():
            logger.error("Backup file not found: {path}", path=backup_path)
            return False

        try:
            encrypted = source.read_bytes().decode("utf-8")
            raw_data = self._crypto.decrypt_bytes(self._key, encrypted)
        except Exception:
            logger.error("Failed to decrypt backup: {path}", path=backup_path)
            return False

        base = self._get_db_base()
        for suffix in ("-wal", "-shm", "-journal"):
            sidecar = Path(str(base) + suffix)
            if sidecar.exists():
                sidecar.unlink()
                logger.info("Removed sidecar file: {name}", name=sidecar.name)

        dest = Path(self._db_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw_data)

        logger.info("Vault restored from encrypted backup: {path}", path=backup_path)
        return True

    def delete_backup(self, backup_path: str) -> bool:
        """Delete a backup file.

        Args:
            backup_path: Path to the backup file.

        Returns:
            True if successful.
        """
        target = Path(backup_path)
        if not target.exists():
            logger.error("Backup file not found for deletion: {path}", path=backup_path)
            return False

        target.unlink()
        logger.info("Deleted backup: {name}", name=target.name)
        return True

    def list_backups(self) -> list[dict]:
        """List all available backups."""
        backups = []
        for f in sorted(self._backup_dir.glob("backup_*.db.bak"), reverse=True):
            backups.append({
                "filename": f.name,
                "path": str(f),
                "size": f.stat().st_size,
                "created_at": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            })
        return backups

    def _cleanup_old_backups(self) -> None:
        """Remove backups exceeding the version limit."""
        backups = sorted(self._backup_dir.glob("backup_*.db.bak"), key=lambda f: f.stat().st_mtime)
        while len(backups) > MAX_BACKUP_VERSIONS:
            oldest = backups.pop(0)
            oldest.unlink()
            logger.info("Removed old backup: {name}", name=oldest.name)
