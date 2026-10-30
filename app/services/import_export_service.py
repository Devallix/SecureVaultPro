"""Import/Export service for SecureVault Pro."""

import csv
import json
import os
from pathlib import Path

from app.core.exceptions import ImportValidationError
from app.logging.logger import get_logger

_MAX_FIELD_LENGTH = 4096

logger = get_logger(__name__)


class ImportExportService:
    """Service for importing and exporting vault data."""

    def __init__(self, vault_key: bytes, password_service, note_service) -> None:
        self._key = vault_key
        self._password_service = password_service
        self._note_service = note_service

    def _sanitize_field(self, value: str | None, max_len: int = _MAX_FIELD_LENGTH) -> str:
        if value is None:
            return ""
        return value[:max_len]

    def export_passwords_csv(self, vault_id: str, output_path: str, encrypt: bool = False) -> int:
        """Export all passwords to a CSV file.

        Args:
            vault_id: The vault ID.
            output_path: Path to write the CSV.
            encrypt: If True, encrypt the output file with the vault key.

        Returns:
            Number of entries exported.
        """
        entries = self._password_service.get_all_passwords(vault_id)
        csv_content = self._build_csv(entries)
        self._write_export(output_path, csv_content, encrypt)
        logger.info("Exported {count} passwords to CSV", count=len(entries))
        return len(entries)

    def _build_csv(self, entries: list[dict]) -> str:
        import io
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["title", "username", "password", "url", "notes"])
        writer.writeheader()
        for entry in entries:
            writer.writerow({
                "title": entry["title"],
                "username": entry["username"],
                "password": entry["password"],
                "url": entry["url"],
                "notes": entry["notes"],
            })
        return buf.getvalue()

    def export_passwords_json(self, vault_id: str, output_path: str, encrypt: bool = False) -> int:
        """Export all passwords to a JSON file.

        Args:
            vault_id: The vault ID.
            output_path: Path to write the JSON.
            encrypt: If True, encrypt the output file with the vault key.

        Returns:
            Number of entries exported.
        """
        entries = self._password_service.get_all_passwords(vault_id)
        data = [
            {
                "title": e["title"],
                "username": e["username"],
                "password": e["password"],
                "url": e["url"],
                "notes": e["notes"],
            }
            for e in entries
        ]
        json_content = json.dumps(data, indent=2)
        self._write_export(output_path, json_content, encrypt)
        logger.info("Exported {count} passwords to JSON", count=len(entries))
        return len(entries)

    def _write_export(self, output_path: str, content: str, encrypt: bool) -> None:
        if encrypt:
            from app.security.crypto_engine import CryptoEngine
            crypto = CryptoEngine()
            encrypted = crypto.encrypt_bytes(self._key, content.encode("utf-8"))
            Path(output_path).write_text(encrypted, encoding="utf-8")
            logger.info("Export encrypted: {path}", path=output_path)
        else:
            Path(output_path).write_text(content, encoding="utf-8")
            logger.warning(
                "Export written as plaintext to {path} — passwords are visible",
                path=output_path,
            )

    def import_passwords_csv(self, vault_id: str, csv_path: str) -> int:
        """Import passwords from a CSV file.

        Expected columns: title, username, password, url, notes

        Returns:
            Number of entries imported.
        """
        import os
        from pathlib import Path

        path = Path(csv_path)
        if not path.is_file():
            raise ImportValidationError(f"File not found: {csv_path}")
        if not path.suffix.lower() in (".csv",):
            raise ImportValidationError(f"Unsupported file type: {path.suffix}")

        count = 0
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    self._password_service.create_password(
                        vault_id=vault_id,
                        title=self._sanitize_field(row.get("title", "Imported")),
                        username=self._sanitize_field(row.get("username", "")),
                        password=self._sanitize_field(row.get("password", "")),
                        url=self._sanitize_field(row.get("url", "")),
                        notes=self._sanitize_field(row.get("notes", "")),
                    )
                    count += 1
                except Exception as e:
                    logger.warning("Failed to import row: {err}", err=str(e)[:200])
        logger.info("Imported {count} passwords from CSV", count=count)
        return count
