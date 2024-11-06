import logging

from config import ALLOWED_CHARS, MAX_LENGTH_WORDPAIR_COMPONENT, MIN_LENGTH_WORDPAIR_COMPONENT
from src.filters.allowed_chars_filter import AllowedCharsFilter
from src.filters.length_filter import LengthFilter
from src.validators.base_validator import ValidatorBase
from text_data import MSG_ERROR_COMPONENT_INVALID_CHARS, MSG_ERROR_COMPONENT_INVALID_LENGTH


class ComponentValidator(ValidatorBase):
    """Валідатор для компонента словникової пари (слово, переклад, транскрипція, анотація)"""

    def __init__(self, component: str, errors: list = None) -> None:
        super().__init__(errors)
        self.logger: logging.Logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

        self._component: str = component

    def _check_valid_length(self) -> bool:
        length_filter = LengthFilter(min_length=MIN_LENGTH_WORDPAIR_COMPONENT,
                                     max_length=MAX_LENGTH_WORDPAIR_COMPONENT)

        if not length_filter.apply(self._component):
            current_length: int = len(self._component)
            self.logger.warning('Компонент містить некоректну кількість символів.'
                                f'Зараз {current_length}, '
                                f'має містити від {MIN_LENGTH_WORDPAIR_COMPONENT} до {MAX_LENGTH_WORDPAIR_COMPONENT}')

            self.add_error(MSG_ERROR_COMPONENT_INVALID_LENGTH.format(min_length=MIN_LENGTH_WORDPAIR_COMPONENT,
                                                                     max_length=MAX_LENGTH_WORDPAIR_COMPONENT))
            return False
        return True

    def _check_valid_allowed_chars(self) -> bool:
        allowed_chars_filter = AllowedCharsFilter(ALLOWED_CHARS)
        if allowed_chars_filter.apply(self._component):
            return True

        self.logger.warning('Компонент містить некоректні символи')
        self.add_error(MSG_ERROR_COMPONENT_INVALID_CHARS.format(allowed_chars=ALLOWED_CHARS))

        return False

    def is_valid(self) -> bool:
        self.logger.info(f'[START-VALIDATOR] Перевірка компонента словникової пари: {self._component}')

        is_valid_length: bool = self._check_valid_length()
        is_valid_chars: bool = self._check_valid_allowed_chars()
        is_valid: bool = is_valid_length and is_valid_chars

        self.logger.info(f'[END-VALIDATOR] Перевірка компонента словникової пари: {self._component}. '
                         f'Компонент {"ВАЛІДНИЙ" if is_valid else "НЕ ВАЛІДНИЙ"}')
        return is_valid
