import logging
from typing import List, Optional

from ..base_validator import ValidatorBase
from sqlalchemy.orm import Session

from config import ALLOWED_CHARS, MAX_LENGTH_VOCAB_NAME, MIN_LENGTH_VOCAB_NAME
from db.models import Vocabulary
from src.filters.allowed_chars_filter import AllowedCharsFilter
from src.filters.valid_length_filter import ValidLengthFilter
from text_data import MSG_ERROR_ALLOWED_CHARS_VOCAB_NAME, MSG_ERROR_LENGTH_VOCAB_NAME, MSG_ERROR_UNIQUE_VOCAB_NAME


class VocabNameValidator(ValidatorBase):
    def __init__(self, name: str, user_id: int, db_session: Session, errors: Optional[List[str]] = None) -> None:
        super().__init__(errors=errors)

        self.name: str = name
        self.user_id: int = user_id
        self.db_session: Session = db_session

        # Фільтри для перевірки
        self.allowed_chars_filter = AllowedCharsFilter(ALLOWED_CHARS)
        self.correct_length_filter = ValidLengthFilter(min_length=MIN_LENGTH_VOCAB_NAME,
                                                       max_length=MAX_LENGTH_VOCAB_NAME)

    def check_unique_name_per_user(self) -> bool:
        """Перевіряє, що назва словника унікальна серед словників користувача"""
        logging.info('VALIDATOR START: "Перевірка унікальності назви словника"')

        existing_vocab: Vocabulary | None = (
            self.db_session.query(Vocabulary)
            .filter(Vocabulary.name.ilike(self.name), Vocabulary.user_id == self.user_id)
            .first())

        if existing_vocab:
            logging.warning(f'Назва словника "{self.name}" вже використовується в базі словників користувача')
            self.add_error(MSG_ERROR_UNIQUE_VOCAB_NAME.format(name=self.name))
            return False
        return True

    def check_valid_length(self) -> bool:
        """Перевіряє, що довжина назви словника коректна"""
        logging.info('VALIDATOR START: "Перевірка довжини назви словника"')

        if not self.correct_length_filter.apply(self.name):
            logging.warning(f'Некоректна довжина назви словника "{self.name}"')
            self.add_error(MSG_ERROR_LENGTH_VOCAB_NAME.format(min_len=MIN_LENGTH_VOCAB_NAME,
                                                              max_len=MAX_LENGTH_VOCAB_NAME))
            return False
        return True

    def check_valid_chars(self) -> bool:
        """Перевіряє, що назва словника містить лише дозволені символи"""
        logging.info('VALIDATOR START: "Перевірка символів у назві словника"')

        if not self.allowed_chars_filter.apply(self.name):
            logging.warning(f'Назва словника "{self.name}" містить некоректні символи')
            self.add_error(MSG_ERROR_ALLOWED_CHARS_VOCAB_NAME.format(allowed_chars=''.join(ALLOWED_CHARS)))
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки й повертає True, якщо всі пройдені"""
        logging.info(f'VALIDATOR START: "Перевірка валідності назви словника {self.name}"')

        is_unique_name_per_user: bool = self.check_unique_name_per_user()
        is_valid_length: bool = self.check_valid_length()
        is_valid_chars: bool = self.check_valid_chars()

        is_valid: bool = is_unique_name_per_user and is_valid_length and is_valid_chars

        logging.info(f'VALIDATOR FINAL: Назва словника {"КОРЕКТНА" if is_valid else "НЕ КОРЕКТНА"}')
        return is_valid
