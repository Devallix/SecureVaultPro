"""Password service for SecureVault Pro.

Handles password CRUD, generation, history, and health analysis.
"""
from __future__ import annotations

import secrets
import string
from typing import TYPE_CHECKING

from app.core.constants import DEFAULT_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH
from app.logging.logger import get_logger
from app.security.crypto_engine import CryptoEngine

if TYPE_CHECKING:
    from app.models.password import Password

logger = get_logger(__name__)


class PasswordService:
    """Service for managing password entries."""

    def __init__(self, vault_key: bytes, password_repo, session) -> None:
        self._key = vault_key
        self._repo = password_repo
        self._session = session
        self._crypto = CryptoEngine()

    def create_password(
        self,
        vault_id: str,
        title: str,
        username: str,
        password: str,
        url: str = "",
        notes: str = "",
        category_id: str | None = None,
        is_favourite: bool = False,
        expires_at=None,
    ) -> Password:
        """Create a new password entry.

        Args:
            vault_id: The vault ID.
            title: Entry title.
            username: Username/email.
            password: The password to store.
            url: Associated URL.
            notes: Additional notes.
            category_id: Category assignment.
            is_favourite: Whether to mark as favourite.

        Returns:
            The created Password model.
        """
        from app.models.password import Password

        password_hash = self._crypto.hash_password_for_storage(password)

        entry = Password(
            vault_id=vault_id,
            title_enc=self._crypto.encrypt_field(self._key, title),
            username_enc=self._crypto.encrypt_field(self._key, username),
            password_enc=self._crypto.encrypt_field(self._key, password),
            password_hash=password_hash,
            url_enc=self._crypto.encrypt_field(self._key, url) if url else None,
            notes_enc=self._crypto.encrypt_field(self._key, notes) if notes else None,
            category_id=category_id,
            is_favourite=is_favourite,
            expires_at=expires_at,
        )
        self._repo.create(entry)
        logger.info("Password entry created: {title}", title=title[:20])
        return entry

    def get_password(self, entry_id: str) -> dict | None:
        """Get and decrypt a password entry.

        Args:
            entry_id: The entry ID.

        Returns:
            Decrypted password data dict, or None.
        """
        entry = self._repo.get_by_id(entry_id)
        if entry is None:
            return None
        return self._decrypt_entry(entry)

    def get_all_passwords(self, vault_id: str) -> list[dict]:
        """Get all decrypted password entries for a vault.

        Args:
            vault_id: The vault ID.

        Returns:
            List of decrypted password dicts.
        """
        entries = self._repo.get_by_vault(vault_id)
        return [self._decrypt_entry(e) for e in entries]

    def get_favourite_passwords(self, vault_id: str) -> list[dict]:
        """Get all favourite password entries for a vault."""
        entries = self._repo.get_favourites(vault_id)
        return [self._decrypt_entry(e) for e in entries]

    def get_passwords_by_category(self, category_id: str) -> list[dict]:
        """Get all password entries in a category."""
        entries = self._repo.get_by_category(category_id)
        return [self._decrypt_entry(e) for e in entries]

    def get_categories(self, vault_id: str) -> list[dict]:
        """Get all categories for a vault."""
        from app.repositories.category_repository import CategoryRepository

        cat_repo = CategoryRepository(self._session)
        cats = cat_repo.get_by_vault(vault_id)
        return [{"id": c.id, "name": c.name, "icon": c.icon} for c in cats]

    def create_category(self, vault_id: str, name: str, icon: str = "") -> dict:
        """Create a new category. Returns the created category dict."""
        from app.models.category import Category
        from app.repositories.category_repository import CategoryRepository

        cat_repo = CategoryRepository(self._session)
        existing = cat_repo.get_by_name(vault_id, name)
        if existing is not None:
            raise ValueError(f"Category '{name}' already exists")

        cat = Category(vault_id=vault_id, name=name, icon=icon or None)
        self._session.add(cat)
        self._session.flush()
        logger.info("Category created: {name}", name=name)
        return {"id": cat.id, "name": cat.name, "icon": cat.icon}

    def update_category(self, category_id: str, name: str | None = None, icon: str | None = None) -> None:
        """Update a category's name or icon."""
        from app.models.category import Category

        cat = self._session.get(Category, category_id)
        if cat is None:
            return
        if name is not None:
            cat.name = name
        if icon is not None:
            cat.icon = icon or None
        self._session.flush()
        logger.info("Category updated: {id}", id=category_id[:8])

    def delete_category(self, category_id: str) -> bool:
        """Delete a category. Passwords in this category become uncategorized."""
        from app.models.category import Category

        cat = self._session.get(Category, category_id)
        if cat is None:
            return False
        for pw in cat.passwords:
            pw.category_id = None
        self._session.delete(cat)
        self._session.flush()
        logger.info("Category deleted: {id}", id=category_id[:8])
        return True

    def get_password_history(self, entry_id: str) -> list[dict]:
        """Get password history for an entry."""
        entry = self._repo.get_by_id(entry_id)
        if entry is None:
            return []
        return [
            {"id": h.id, "password_hash": h.password_hash, "created_at": h.created_at}
            for h in entry.history
        ]

    def update_password(self, entry_id: str, **kwargs) -> None:
        """Update a password entry.

        Args:
            entry_id: The entry ID.
            **kwargs: Fields to update (title, username, password, etc.).
        """
        entry = self._repo.get_by_id(entry_id)
        if entry is None:
            return

        if "password" in kwargs:
            old_entry = self._decrypt_entry(entry)
            self._add_to_history(entry, old_entry.get("password", ""))

        if "title" in kwargs:
            entry.title_enc = self._crypto.encrypt_field(self._key, kwargs["title"])
        if "username" in kwargs:
            entry.username_enc = self._crypto.encrypt_field(self._key, kwargs["username"])
        if "password" in kwargs:
            entry.password_enc = self._crypto.encrypt_field(self._key, kwargs["password"])
            entry.password_hash = self._crypto.hash_password_for_storage(kwargs["password"])
        if "url" in kwargs:
            entry.url_enc = self._crypto.encrypt_field(self._key, kwargs["url"]) if kwargs["url"] else None
        if "notes" in kwargs:
            entry.notes_enc = self._crypto.encrypt_field(self._key, kwargs["notes"]) if kwargs["notes"] else None
        if "is_favourite" in kwargs:
            entry.is_favourite = kwargs["is_favourite"]
        if "category_id" in kwargs:
            entry.category_id = kwargs["category_id"]
        if "expires_at" in kwargs:
            entry.expires_at = kwargs["expires_at"]

        self._repo.update(entry)
        logger.info("Password entry updated: {id}", id=entry_id[:8])

    def delete_password(self, entry_id: str) -> bool:
        """Delete a password entry.

        Args:
            entry_id: The entry ID.

        Returns:
            True if deleted.
        """
        result = self._repo.delete_by_id(entry_id)
        if result:
            logger.info("Password entry deleted: {id}", id=entry_id[:8])
        return result

    def _decrypt_entry(self, entry) -> dict:
        """Decrypt a password entry model into a dict."""
        return {
            "id": entry.id,
            "title": self._crypto.decrypt_field(self._key, entry.title_enc),
            "username": self._crypto.decrypt_field(self._key, entry.username_enc) if entry.username_enc else "",
            "password": self._crypto.decrypt_field(self._key, entry.password_enc),
            "url": self._crypto.decrypt_field(self._key, entry.url_enc) if entry.url_enc else "",
            "notes": self._crypto.decrypt_field(self._key, entry.notes_enc) if entry.notes_enc else "",
            "is_favourite": entry.is_favourite,
            "category_id": entry.category_id,
            "expires_at": entry.expires_at,
            "created_at": entry.created_at,
            "updated_at": entry.updated_at,
        }

    def _add_to_history(self, entry, old_password: str) -> None:
        """Add the old password to history."""
        from app.models.password_history import PasswordHistory

        if not old_password:
            return
        history = PasswordHistory(
            password_id=entry.id,
            password_hash=self._crypto.hash_password_for_storage(old_password),
        )
        self._session.add(history)

    @staticmethod
    def generate_password(
        length: int = DEFAULT_PASSWORD_LENGTH,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
    ) -> str:
        """Generate a cryptographically random password.

        Args:
            length: Password length.
            use_uppercase: Include A-Z.
            use_lowercase: Include a-z.
            use_digits: Include 0-9.
            use_symbols: Include special characters.

        Returns:
            Generated password string.
        """
        length = max(MIN_PASSWORD_LENGTH, min(MAX_PASSWORD_LENGTH, length))
        chars = ""
        if use_uppercase:
            chars += string.ascii_uppercase
        if use_lowercase:
            chars += string.ascii_lowercase
        if use_digits:
            chars += string.digits
        if use_symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if not chars:
            chars = string.ascii_letters + string.digits

        return "".join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def generate_passphrase(
        num_words: int = 4,
        separator: str = "-",
        capitalize: bool = True,
    ) -> str:
        """Generate a BIP39-style passphrase from random words.

        Args:
            num_words: Number of words (3-8).
            separator: Word separator character.
            capitalize: Whether to capitalize each word.

        Returns:
            Generated passphrase string.
        """
        from app.security.secure_random import _BIP39_WORDS

        num_words = max(3, min(8, num_words))
        words = [secrets.choice(_BIP39_WORDS) for _ in range(num_words)]
        if capitalize:
            words = [w.capitalize() for w in words]
        return separator.join(words)

    @staticmethod
    def calculate_strength(password: str) -> dict:
        """Calculate password strength metrics.

        Args:
            password: The password to evaluate.

        Returns:
            Dict with score, entropy, and label.
        """
        score = 0
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1

        pool = 0
        if any(c.isupper() for c in password):
            pool += 26
        if any(c.islower() for c in password):
            pool += 26
        if any(c.isdigit() for c in password):
            pool += 10
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            pool += 32

        import math
        entropy = len(password) * math.log2(max(pool, 1)) if pool > 0 else 0

        if score <= 2:
            label = "Weak"
        elif score <= 4:
            label = "Fair"
        elif score <= 5:
            label = "Good"
        else:
            label = "Strong"

        return {"score": score, "max_score": 7, "entropy": round(entropy, 1), "label": label}
