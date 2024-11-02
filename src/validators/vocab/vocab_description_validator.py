import logging

from ..base_validator import ValidatorBase

from config import MAX_LENGTH_VOCAB_DESCRIPTION, MIN_LENGTH_VOCAB_DESCRIPTION
from src.filters.valid_length_filter import ValidLengthFilter
from text_data import MSG_ERROR_LENGTH_VOCAB_DESCRIPTION


class VocabDescriptionValidator(ValidatorBase):
    def __init__(self, description: str, errors: list = None) -> None:
        super().__init__(errors)

        self._description: str = description

        # Фільтри для перевірки
        self.valid_length_filter = ValidLengthFilter(min_length=MIN_LENGTH_VOCAB_DESCRIPTION,
                                                     max_length=MAX_LENGTH_VOCAB_DESCRIPTION)

    def check_valid_length(self) -> bool:
        """Перевіряє, що кількість символів опису словника коректна"""
        logging.info('VALIDATOR START: "Перевірка опису словника"')

        if not self.valid_length_filter.apply(self._description):
            logging.warning(f'Не валідна кількість символів опису словника: "{self._description}"')
            self.add_error(MSG_ERROR_LENGTH_VOCAB_DESCRIPTION.format(min_len=MIN_LENGTH_VOCAB_DESCRIPTION,
                                                                     max_len=MAX_LENGTH_VOCAB_DESCRIPTION))
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        logging.info(f'VALIDATOR START: "Перевірка валідності опису словника: {self._description}"')

        is_valid_length: bool = self.check_valid_length()

        is_valid: bool = is_valid_length

        logging.info(f'VALIDATOR FINAL: Опис словника {"ВАЛІДНИЙ" if is_valid else "НЕ ВАЛІДНИЙ"}')
        return is_valid
