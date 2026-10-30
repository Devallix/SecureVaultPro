"""Notes ViewModel."""

from PySide6.QtCore import QObject, Signal


class NotesViewModel(QObject):
    """ViewModel for secure notes."""

    notes_loaded = Signal(list)
    note_selected = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, note_service, parent=None) -> None:
        super().__init__(parent)
        self._service = note_service
        self._vault_id: str | None = None

    def set_vault(self, vault_id: str) -> None:
        self._vault_id = vault_id
        self.load_notes()

    def load_notes(self) -> None:
        if self._vault_id is None:
            return
        try:
            notes = self._service.get_all_notes(self._vault_id)
            self.notes_loaded.emit(notes)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def select_note(self, note_id: str) -> None:
        note = self._service.get_note(note_id)
        if note:
            self.note_selected.emit(note)

    def create_note(self, title: str, content: str) -> None:
        if self._vault_id is None:
            return
        try:
            self._service.create_note(self._vault_id, title, content)
            self.load_notes()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def update_note(self, note_id: str, content: str) -> None:
        try:
            self._service.update_note(note_id, content=content)
            self.load_notes()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def delete_note(self, note_id: str) -> None:
        try:
            self._service.delete_note(note_id)
            self.load_notes()
        except Exception as e:
            self.error_occurred.emit(str(e))
