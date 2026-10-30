"""Settings repository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_settings import UserSetting
from app.repositories.base_repository import BaseRepository


class SettingsRepository(BaseRepository[UserSetting]):
    """Repository for user settings data access."""

    def __init__(self, session: Session) -> None:
        super().__init__(UserSetting, session)

    def get_by_vault_and_key(self, vault_id: str, key: str) -> UserSetting | None:
        """Get a setting by vault and key."""
        stmt = select(UserSetting).where(
            UserSetting.vault_id == vault_id,
            UserSetting.key == key,
        )
        return self.session.execute(stmt).scalars().first()

    def get_all_by_vault(self, vault_id: str) -> list[UserSetting]:
        """Get all settings for a vault."""
        stmt = select(UserSetting).where(UserSetting.vault_id == vault_id)
        return list(self.session.execute(stmt).scalars().all())

    def set_value(self, vault_id: str, key: str, value_enc: str) -> UserSetting:
        """Set a setting value, creating or updating as needed."""
        existing = self.get_by_vault_and_key(vault_id, key)
        if existing:
            existing.value_enc = value_enc
            self.session.flush()
            return existing
        setting = UserSetting(vault_id=vault_id, key=key, value_enc=value_enc)
        return self.create(setting)
