"""Digital identity ViewModel."""

from PySide6.QtCore import QObject, Signal

from app.logging.logger import get_logger
from app.security.crypto_engine import CryptoEngine

logger = get_logger(__name__)


class DigitalIdentityViewModel(QObject):
    """ViewModel for SSH keys, API keys, and software licences."""

    ssh_keys_loaded = Signal(list)
    api_keys_loaded = Signal(list)
    licences_loaded = Signal(list)
    ssh_key_detail_loaded = Signal(dict)
    api_key_detail_loaded = Signal(dict)
    licence_detail_loaded = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, ssh_key_repo, api_key_repo, licence_repo, vault_key, parent=None) -> None:
        super().__init__(parent)
        self._ssh_repo = ssh_key_repo
        self._api_repo = api_key_repo
        self._licence_repo = licence_repo
        self._key = vault_key
        self._crypto = CryptoEngine()
        self._vault_id: str | None = None

    def set_vault(self, vault_id: str) -> None:
        self._vault_id = vault_id
        self.load_all()

    def load_all(self) -> None:
        self.load_ssh_keys()
        self.load_api_keys()
        self.load_licences()

    def load_ssh_keys(self) -> None:
        if self._vault_id is None:
            return
        try:
            entries = self._ssh_repo.get_by_vault(self._vault_id)
            result = [
                {
                    "id": e.id,
                    "name": self._crypto.decrypt_field(self._key, e.name_enc),
                    "key_type": e.key_type,
                    "fingerprint": e.fingerprint,
                    "last_used_at": e.last_used_at,
                }
                for e in entries
            ]
            self.ssh_keys_loaded.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def load_api_keys(self) -> None:
        if self._vault_id is None:
            return
        try:
            entries = self._api_repo.get_by_vault(self._vault_id)
            result = [
                {
                    "id": e.id,
                    "name": self._crypto.decrypt_field(self._key, e.name_enc),
                    "service": self._crypto.decrypt_field(self._key, e.service_enc) if e.service_enc else "",
                    "expires_at": e.expires_at,
                    "last_used_at": e.last_used_at,
                }
                for e in entries
            ]
            self.api_keys_loaded.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def load_licences(self) -> None:
        if self._vault_id is None:
            return
        try:
            entries = self._licence_repo.get_by_vault(self._vault_id)
            result = [
                {
                    "id": e.id,
                    "name": self._crypto.decrypt_field(self._key, e.name_enc),
                    "publisher": self._crypto.decrypt_field(self._key, e.publisher_enc) if e.publisher_enc else "",
                    "expires_at": e.expires_at,
                }
                for e in entries
            ]
            self.licences_loaded.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def get_ssh_key(self, key_id: str) -> None:
        if self._vault_id is None:
            return
        try:
            entry = self._ssh_repo.get_by_id(key_id)
            if entry is None:
                return
            result = {
                "id": entry.id,
                "name": self._crypto.decrypt_field(self._key, entry.name_enc),
                "key_type": entry.key_type,
                "fingerprint": entry.fingerprint,
                "public_key": self._crypto.decrypt_field(self._key, entry.public_key_enc),
                "private_key": self._crypto.decrypt_field(self._key, entry.private_key_enc),
                "last_used_at": entry.last_used_at,
            }
            self.ssh_key_detail_loaded.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def get_api_key(self, key_id: str) -> None:
        if self._vault_id is None:
            return
        try:
            entry = self._api_repo.get_by_id(key_id)
            if entry is None:
                return
            result = {
                "id": entry.id,
                "name": self._crypto.decrypt_field(self._key, entry.name_enc),
                "service": self._crypto.decrypt_field(self._key, entry.service_enc) if entry.service_enc else "",
                "key_value": self._crypto.decrypt_field(self._key, entry.key_value_enc),
                "expires_at": entry.expires_at,
                "last_used_at": entry.last_used_at,
            }
            self.api_key_detail_loaded.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def get_licence(self, key_id: str) -> None:
        if self._vault_id is None:
            return
        try:
            entry = self._licence_repo.get_by_id(key_id)
            if entry is None:
                return
            result = {
                "id": entry.id,
                "name": self._crypto.decrypt_field(self._key, entry.name_enc),
                "publisher": self._crypto.decrypt_field(self._key, entry.publisher_enc) if entry.publisher_enc else "",
                "licence_key": self._crypto.decrypt_field(self._key, entry.licence_key_enc),
                "expires_at": entry.expires_at,
            }
            self.licence_detail_loaded.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def add_ssh_key(self, name: str, key_type: str, fingerprint: str, public_key: str, private_key: str) -> None:
        if self._vault_id is None:
            return
        try:
            from app.models.ssh_key import SSHKey

            ssh_key = SSHKey(
                vault_id=self._vault_id,
                name_enc=self._crypto.encrypt_field(self._key, name),
                public_key_enc=self._crypto.encrypt_field(self._key, public_key),
                private_key_enc=self._crypto.encrypt_field(self._key, private_key),
                key_type=key_type,
                fingerprint=fingerprint,
            )
            self._ssh_repo.create(ssh_key)
            logger.info("SSH key added: {name}", name=name)
            self.load_ssh_keys()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def add_api_key(self, name: str, service: str, key_value: str) -> None:
        if self._vault_id is None:
            return
        try:
            from app.models.api_key import APIKey

            api_key = APIKey(
                vault_id=self._vault_id,
                name_enc=self._crypto.encrypt_field(self._key, name),
                key_value_enc=self._crypto.encrypt_field(self._key, key_value),
                service_enc=self._crypto.encrypt_field(self._key, service) if service else None,
            )
            self._api_repo.create(api_key)
            logger.info("API key added: {name}", name=name)
            self.load_api_keys()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def add_licence(self, name: str, publisher: str, licence_key: str) -> None:
        if self._vault_id is None:
            return
        try:
            from app.models.software_licence import SoftwareLicence

            licence = SoftwareLicence(
                vault_id=self._vault_id,
                name_enc=self._crypto.encrypt_field(self._key, name),
                licence_key_enc=self._crypto.encrypt_field(self._key, licence_key),
                publisher_enc=self._crypto.encrypt_field(self._key, publisher) if publisher else None,
            )
            self._licence_repo.create(licence)
            logger.info("Software licence added: {name}", name=name)
            self.load_licences()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def delete_ssh_key(self, key_id: str) -> None:
        try:
            self._ssh_repo.delete_by_id(key_id)
            self.load_ssh_keys()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def delete_api_key(self, key_id: str) -> None:
        try:
            self._api_repo.delete_by_id(key_id)
            self.load_api_keys()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def delete_licence(self, licence_id: str) -> None:
        try:
            self._licence_repo.delete_by_id(licence_id)
            self.load_licences()
        except Exception as e:
            self.error_occurred.emit(str(e))
