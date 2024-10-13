from .base_validator import ValidatorBase

from config import MAX_LENGTH_VOCAB_NOTE, MIN_LENGTH_VOCAB_NOTE
from src.filters.length_filter import LengthFilter


class VocabNoteValidator(ValidatorBase):
    def __init__(self, note: str) -> None:
        super().__init__()  # Виклик конструктора базового класу

        self.note: str = note  # Примітка до словника

    def check_valid_length(self) -> bool:
        """Перевіряє, що коректна довжини"""
        length_vocab_note: int = len(self.note)  # Довжина назви словника

        length_filter = LengthFilter(min_length=MIN_LENGTH_VOCAB_NOTE, max_length=MAX_LENGTH_VOCAB_NOTE)
        if not length_filter.apply(value=self.note):
            error_text: str = (
                f'Назва словника має містити від {MIN_LENGTH_VOCAB_NOTE} до {MAX_LENGTH_VOCAB_NOTE} символів.')
            log_text: str = (
                f'Примітка до словника "{self.note}" не відповідає вимогам по довжині: '
                f'довжина {length_vocab_note} символів. '
                f'Допустима довжина: від {MIN_LENGTH_VOCAB_NOTE} до {MAX_LENGTH_VOCAB_NOTE}')
            self.add_error_with_log(error_text, log_text)  # Додавання помилок та виведення логування
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        checks: list[bool] = [self.check_valid_length()]
        return all(checks)
