import logging

from config import MAX_LENGTH_VOCAB_DESCRIPTION, MIN_LENGTH_VOCAB_DESCRIPTION
from src.filters.length_filter import LengthFilter
from src.validators.base_validator import ValidatorBase
from text_data import MSG_ERROR_VOCAB_DESCRIPTION_INVALID_LENGTH


class VocabDescriptionValidator(ValidatorBase):
    def __init__(self, description: str, errors: list = None) -> None:
        super().__init__(errors)
        self.logger: logging.Logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

        self._description: str = description

    def _check_valid_length(self) -> bool:
        length_filter = LengthFilter(min_length=MIN_LENGTH_VOCAB_DESCRIPTION,
                                     max_length=MAX_LENGTH_VOCAB_DESCRIPTION)

        if not length_filter.apply(self._description):
            current_length: int = len(self._description)
            self.logger.warning('Опис словника містить некоректну кількість символів.'
                                f'Зараз {current_length}, '
                                f'має містити від {MIN_LENGTH_VOCAB_DESCRIPTION} до {MAX_LENGTH_VOCAB_DESCRIPTION}')
            self.add_error(MSG_ERROR_VOCAB_DESCRIPTION_INVALID_LENGTH.format(min_length=MIN_LENGTH_VOCAB_DESCRIPTION,
                                                                             max_length=MAX_LENGTH_VOCAB_DESCRIPTION))
            return False
        return True

    def is_valid(self) -> bool:
        self.logger.info(f'[START-VALIDATOR] Перевірка опису словника: {self._description}')

        is_valid_length: bool = self._check_valid_length()
        is_valid: bool = is_valid_length

        self.logger.info(f'[END-VALIDATOR] Перевірка опису словника: {self._description}. '
                         f'Опис словника {"ВАЛІДНИЙ" if is_valid else "НЕ ВАЛІДНИЙ"}')
        return is_valid
