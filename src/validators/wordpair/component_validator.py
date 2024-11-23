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
        """Перевіряє, чи містить компонент коректну кількість символів"""
        length_filter = LengthFilter(min_length=MIN_LENGTH_WORDPAIR_COMPONENT,
                                     max_length=MAX_LENGTH_WORDPAIR_COMPONENT)

        if not length_filter.apply(self._component):
            current_length: int = len(self._component)
            self.logger.warning(f'Компонент "{self._component}" містить некоректну кількість символів. '
                                f'Зараз {current_length}, '
                                f'має містити від {MIN_LENGTH_WORDPAIR_COMPONENT} до {MAX_LENGTH_WORDPAIR_COMPONENT}')

            self.add_error(MSG_ERROR_COMPONENT_INVALID_LENGTH.format(component=self._component,
                                                                     min_length=MIN_LENGTH_WORDPAIR_COMPONENT,
                                                                     max_length=MAX_LENGTH_WORDPAIR_COMPONENT))
            return False
        return True

    def _check_valid_chars(self) -> bool:
        """Перевіряє, чи не містить назва некоректні символи"""
        allowed_chars_filter = AllowedCharsFilter(ALLOWED_CHARS)

        if not allowed_chars_filter.apply(self._component):
            self.logger.warning(f'Компонент "{self._component}" містить некоректні символи')
            self.add_error(MSG_ERROR_COMPONENT_INVALID_CHARS.format(component=self._component,
                                                                    allowed_chars=ALLOWED_CHARS))
            return False
        return True

    def is_valid(self) -> bool:
        """Виконує всі перевірки для компонента, та повертає прапор, чи успішно пройдені всі перевірки"""
        is_valid_length: bool = self._check_valid_length()
        is_valid_chars: bool = self._check_valid_chars()
        is_valid: bool = is_valid_length and is_valid_chars

        if not is_valid:
            self.logger.warning(f'Компонент "{self._component}" НЕ ВАЛІДНИЙ')
        return is_valid
