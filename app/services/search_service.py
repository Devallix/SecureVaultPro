"""Search service for SecureVault Pro."""

from app.logging.logger import get_logger
from app.security.crypto_engine import CryptoEngine

logger = get_logger(__name__)


class SearchService:
    """Service for global search across all vault entities."""

    def __init__(self, vault_key: bytes, password_repo, note_repo, file_repo) -> None:
        self._key = vault_key
        self._password_repo = password_repo
        self._note_repo = note_repo
        self._file_repo = file_repo
        self._crypto = CryptoEngine()

    def search(self, vault_id: str, query: str) -> list[dict]:
        """Search across all entity types.

        Args:
            vault_id: The vault ID.
            query: Search query string.

        Returns:
            List of matching results with type and metadata.
        """
        results = []
        query_lower = query.lower()

        passwords = self._password_repo.get_by_vault(vault_id, limit=500)
        for p in passwords:
            try:
                title = self._crypto.decrypt_field(self._key, p.title_enc)
                username = self._crypto.decrypt_field(self._key, p.username_enc) if p.username_enc else ""
                if query_lower in title.lower() or query_lower in username.lower():
                    results.append({
                        "type": "password",
                        "id": p.id,
                        "title": title,
                        "subtitle": username,
                    })
            except Exception:
                continue

        notes = self._note_repo.get_by_vault(vault_id, limit=500)
        for n in notes:
            try:
                title = self._crypto.decrypt_field(self._key, n.title_enc)
                content = self._crypto.decrypt_field(self._key, n.content_enc)
                if query_lower in title.lower() or query_lower in content.lower():
                    results.append({
                        "type": "note",
                        "id": n.id,
                        "title": title,
                        "subtitle": content[:80] + "..." if len(content) > 80 else content,
                    })
            except Exception:
                continue

        files = self._file_repo.get_by_vault(vault_id, limit=500)
        for f in files:
            try:
                name = self._crypto.decrypt_field(self._key, f.original_name_enc)
                if query_lower in name.lower():
                    results.append({
                        "type": "file",
                        "id": f.id,
                        "title": name,
                        "subtitle": f"{f.file_size} bytes",
                    })
            except Exception:
                continue

        return results
