from tools.read_data import app_data


class VocabNoteValidator:
    def __init__(self, note: str,
                 min_length: int,
                 max_length: int) -> None:
        self.note: str = note
        self.errors: list = []
        self.min_length_vocab_note: int = min_length
        self.max_length_vocab_note: int = max_length

    def _add_error(self, error_text: str) -> None:
        """Додає помилку до списку"""
        self.errors.append(error_text)

    def correct_length(self) -> bool:
        """Перевіряє, що коректна довжина примітки"""
        if not (self.min_length_vocab_note <= len(self.note) <= self.max_length_vocab_note):
            self._add_error(app_data['create_vocab']['note']['errors']['incorrect_length'].
                            format(self.min_length_vocab_note,
                                   self.max_length_vocab_note))
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        self.errors = []  # Очищуємо помилки перед перевіркою
        checks: list[bool] = [self.correct_length()]
        return all(checks)
