"""Password ViewModel for the password vault view."""

from PySide6.QtCore import QObject, Signal


class PasswordViewModel(QObject):
    """ViewModel for password list and detail views."""

    passwords_loaded = Signal(list)
    password_selected = Signal(dict)
    password_created = Signal(dict)
    password_deleted = Signal(str)
    password_history_loaded = Signal(list)
    categories_loaded = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, password_service, parent=None) -> None:
        super().__init__(parent)
        self._service = password_service
        self._vault_id: str | None = None
        self._favourites_only = False
        self._category_id: str = ""

    def set_vault(self, vault_id: str) -> None:
        self._vault_id = vault_id
        self.load_passwords()
        self.load_categories()

    def load_passwords(self, favourites_only: bool = False, category_id: str = "") -> None:
        if self._vault_id is None:
            return
        self._favourites_only = favourites_only
        self._category_id = category_id
        try:
            if favourites_only:
                entries = self._service.get_favourite_passwords(self._vault_id)
            elif category_id:
                entries = self._service.get_passwords_by_category(category_id)
            else:
                entries = self._service.get_all_passwords(self._vault_id)
            self.passwords_loaded.emit(entries)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def select_password(self, entry_id: str) -> None:
        if entry_id == "__refresh__":
            self.load_passwords(self._favourites_only, self._category_id)
            return
        entry = self._service.get_password(entry_id)
        if entry:
            self.password_selected.emit(entry)
            self.load_password_history(entry_id)

    def create_password(self, title: str, username: str, password: str, url: str = "", notes: str = "", expires_at=None, category_id: str = "") -> None:
        try:
            self._service.create_password(self._vault_id, title, username, password, url, notes, expires_at=expires_at, category_id=category_id or None)
            self.load_passwords()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def update_password(self, entry_id: str, **kwargs) -> None:
        try:
            self._service.update_password(entry_id, **kwargs)
            self.load_passwords()
            entry = self._service.get_password(entry_id)
            if entry:
                self.password_selected.emit(entry)
            self.load_password_history(entry_id)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def delete_password(self, entry_id: str) -> None:
        if self._service.delete_password(entry_id):
            self.password_deleted.emit(entry_id)
            self.load_passwords()

    def toggle_favourite(self, entry_id: str, is_favourite: bool) -> None:
        try:
            self._service.update_password(entry_id, is_favourite=is_favourite)
            self.load_passwords()
            entry = self._service.get_password(entry_id)
            if entry:
                self.password_selected.emit(entry)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def load_categories(self) -> None:
        if self._vault_id is None:
            return
        try:
            cats = self._service.get_categories(self._vault_id)
            self.categories_loaded.emit(cats)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def create_category(self, name: str) -> None:
        if self._vault_id is None:
            return
        try:
            self._service.create_category(self._vault_id, name)
            self.load_categories()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def update_category(self, category_id: str, name: str) -> None:
        try:
            self._service.update_category(category_id, name=name)
            self.load_categories()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def delete_category(self, category_id: str) -> None:
        try:
            self._service.delete_category(category_id)
            self.load_categories()
            self.load_passwords(self._favourites_only, self._category_id)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def load_password_history(self, entry_id: str) -> None:
        try:
            history = self._service.get_password_history(entry_id)
            self.password_history_loaded.emit(history)
        except Exception as e:
            self.error_occurred.emit(str(e))
