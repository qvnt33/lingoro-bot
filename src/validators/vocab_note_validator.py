from .base_validator import ValidatorBase

from config import MAX_LENGTH_VOCAB_NOTE, MIN_LENGTH_VOCAB_NOTE


class VocabNoteValidator(ValidatorBase):
    def __init__(self,
                 note: str,
                 vocab_name: str) -> None:
        super().__init__()  # Виклик конструктора базового класу

        self.note: str = note  # Примітка до словника
        self.vocab_name: str = vocab_name  # Назва словника

    def check_valid_length(self) -> bool:
        """Перевіряє, що коректна довжини"""
        length_vocab_note: int = len(self.name)  # Довжина назви словника
        # Коректна довжина
        is_valid_length: bool = MIN_LENGTH_VOCAB_NOTE <= length_vocab_note <= MAX_LENGTH_VOCAB_NOTE
        if not is_valid_length:
            error_text: str = (
                f'Назва словника має містити від {MIN_LENGTH_VOCAB_NOTE} до {MAX_LENGTH_VOCAB_NOTE} символів.')
            log_text: str = (
                f'Примітка до словника "{self.name}" не відповідає вимогам по довжині: '
                f'довжина {length_vocab_note} символів. '
                f'Допустима довжина: від {MIN_LENGTH_VOCAB_NOTE} до {MAX_LENGTH_VOCAB_NOTE}')
            self.add_error_with_log(error_text, log_text)  # Додавання помилок та виведення логування
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        checks: list[bool] = [self.check_valid_length()]
        return all(checks)
