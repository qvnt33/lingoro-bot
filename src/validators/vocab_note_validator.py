import logging

from .base_validator import ValidatorBase

from config import MAX_LENGTH_VOCAB_NOTE, MIN_LENGTH_VOCAB_NOTE
from src.filters.length_filter import LengthFilter


class VocabNoteValidator(ValidatorBase):
    def __init__(self, note: str, errors_lst: list = None) -> None:
        super().__init__(errors_lst)

        self.note: str = note  # Примітка до словника

        # Фільтри
        self.length_filter = LengthFilter(min_length=MIN_LENGTH_VOCAB_NOTE, max_length=MAX_LENGTH_VOCAB_NOTE)

    def check_valid_length(self) -> bool:
        """Перевіряє, що довжина примітки до словника коректна"""
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "Довжина примітки до словника коректна"')

        is_valid_length: bool = self.length_filter.apply(self.note)  # Чи коректна довжина

        if not is_valid_length:
            logging.warning(f'Некоректна кількість символів у примітці до словника "{self.note}"')
            self.add_validator_error(
                'Довжина примітки до словника має бути від '
                f'{MIN_LENGTH_VOCAB_NOTE} до {MAX_LENGTH_VOCAB_NOTE} символів.')
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        if self.check_valid_length():
            logging.info('ПЕРЕВІРКА ПРОЙДЕНА: "Довжина примітки до словника коректна"')
        else:
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "Довжина примітки до словника коректна"')
            return False
        return True
