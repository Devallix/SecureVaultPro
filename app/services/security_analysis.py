"""Security analysis service for SecureVault Pro.

Analyses password health, detects weak/duplicate/reused passwords,
and provides actionable security recommendations.
"""

from collections import Counter
from datetime import datetime, timedelta

from app.logging.logger import get_logger

logger = get_logger(__name__)


class SecurityAnalysisService:
    """Service for analysing vault security health."""

    def __init__(self, vault_key: bytes, password_repo, password_service) -> None:
        self._key = vault_key
        self._password_repo = password_repo
        self._password_service = password_service

    def analyse_vault(self, vault_id: str) -> dict:
        """Perform a full security analysis of a vault.

        Returns:
            Dict with analysis results and recommendations.
        """
        entries = self._password_repo.get_by_vault(vault_id, limit=10000)
        total = len(entries)

        weak = []
        old = []
        duplicates = []
        hash_counts: Counter = Counter()

        for entry in entries:
            decrypted = self._password_service._decrypt_entry(entry)
            strength = self._password_service.calculate_strength(decrypted["password"])

            if strength["score"] <= 2:
                weak.append({
                    "id": entry.id,
                    "title": decrypted["title"],
                    "strength": strength,
                })

            if entry.updated_at and entry.updated_at < datetime.now() - timedelta(days=90):
                old.append({
                    "id": entry.id,
                    "title": decrypted["title"],
                    "last_updated": entry.updated_at.isoformat(),
                })

            hash_counts[entry.password_hash] += 1

        for hash_val, count in hash_counts.items():
            if count > 1:
                for entry in entries:
                    if entry.password_hash == hash_val:
                        decrypted = self._password_service._decrypt_entry(entry)
                        duplicates.append({
                            "id": entry.id,
                            "title": decrypted["title"],
                            "shared_count": count,
                        })
                        break

        recommendations = []
        if weak:
            recommendations.append(f"Change {len(weak)} weak password(s)")
        if old:
            recommendations.append(f"Update {len(old)} password(s) older than 90 days")
        if duplicates:
            recommendations.append(f"Unique passwords needed for {len(duplicates)} duplicate(s)")

        health_score = 100 if total == 0 else max(0, 100 - (len(weak) * 5 + len(old) * 2 + len(duplicates) * 10))

        return {
            "total_passwords": total,
            "weak_passwords": weak,
            "old_passwords": old,
            "duplicate_passwords": duplicates,
            "health_score": health_score,
            "recommendations": recommendations,
        }
