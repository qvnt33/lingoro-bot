import logging

from sqlalchemy.orm import Session

from config import ALLOWED_CHARS, MAX_LENGTH_VOCAB_NAME, MIN_LENGTH_VOCAB_NAME
from db.models import Vocabulary
from src.filters.allowed_chars_filter import AllowedCharsFilter
from src.filters.length_filter import LengthFilter
from src.validators.base_validator import ValidatorBase
from text_data import (
    MSG_ERROR_COMPONENT_INVALID_CHARS,
    MSG_ERROR_VOCAB_NAME_INVALID_LENGTH,
    MSG_ERROR_VOCAB_NAME_UNIQUELY,
)


class VocabNameValidator(ValidatorBase):
    def __init__(self, name: str, user_id: int, db_session: Session, errors: list = None) -> None:
        super().__init__(errors)
        self.logger: logging.Logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

        self._name: str = name
        self.user_id: int = user_id
        self.db_session: Session = db_session

    def _check_unique_name_per_user(self) -> bool:
        existing_vocab: Vocabulary | None = (
            self.db_session.query(Vocabulary)
            .filter(Vocabulary.name.ilike(self._name), Vocabulary.user_id == self.user_id)
            .first())

        if existing_vocab is not None:
            self.logger.warning('Назва словника вже використовується в базі словників користувача')
            self.add_error(MSG_ERROR_VOCAB_NAME_UNIQUELY.format(name=self._name))
            return False
        return True

    def _check_valid_length(self) -> bool:
        length_filter = LengthFilter(min_length=MIN_LENGTH_VOCAB_NAME,
                                     max_length=MAX_LENGTH_VOCAB_NAME)

        if not length_filter.apply(self._name):
            current_length: int = len(self._name)
            self.logger.warning('Назва словника містить некоректну кількість символів.'
                                f'Зараз {current_length}, '
                                f'має містити від {MIN_LENGTH_VOCAB_NAME} до {MAX_LENGTH_VOCAB_NAME}')
            self.add_error(MSG_ERROR_VOCAB_NAME_INVALID_LENGTH.format(min_len=MIN_LENGTH_VOCAB_NAME,
                                                                      max_len=MAX_LENGTH_VOCAB_NAME))
            return False
        return True

    def _check_valid_chars(self) -> bool:
        allowed_chars_filter = AllowedCharsFilter(ALLOWED_CHARS)

        if not allowed_chars_filter.apply(self._name):
            self.logger.warning('Назва словника містить некоректні символи')
            self.add_error(MSG_ERROR_COMPONENT_INVALID_CHARS.format(allowed_chars=ALLOWED_CHARS))
            return False
        return True

    def is_valid(self) -> bool:
        self.logger.info(f'[START-VALIDATOR] Перевірка назви словника: {self._name}')

        is_unique_name_per_user: bool = self._check_unique_name_per_user()
        is_valid_length: bool = self._check_valid_length()
        is_valid_chars: bool = self._check_valid_chars()
        is_valid: bool = is_unique_name_per_user and is_valid_length and is_valid_chars

        self.logger.info(f'[END-VALIDATOR] Перевірка назви словника: {self._name}. '
                         f'Назва словника {"ВАЛІДНА" if is_valid else "НЕ ВАЛІДНА"}')
        return is_valid
