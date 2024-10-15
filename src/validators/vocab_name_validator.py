import sqlalchemy
from .base_validator import ValidatorBase
from sqlalchemy.orm.query import Query

from config import ALLOWED_CHARACTERS, MAX_LENGTH_VOCAB_NAME, MIN_LENGTH_VOCAB_NAME
from db.models import Vocabulary
from src.filters.allowed_chars_filter import AllowedCharactersFilter
from src.filters.length_filter import LengthFilter


class VocabNameValidator(ValidatorBase):
    def __init__(self,
                 vocab_name: str,
                 user_id: int,
                 db_session: sqlalchemy.orm.session.Session,
                 errors_lst: list = None) -> None:
        super().__init__(errors_lst)
        self.name: str = vocab_name  # Назва словника
        self.user_id: int = user_id  # ID користувача
        self.db_session: sqlalchemy.orm.session.Session = db_session  # БД сесія

    def check_unique_name_per_user(self) -> bool:
        """Перевіряє, що назва словника унікальна серед словників користувача (незалежно від регістру)"""
        is_existing_vocab: Query[Vocabulary] | None = self.db_session.query(Vocabulary).filter(
            Vocabulary.name.ilike(self.name),
            Vocabulary.user_id == self.user_id).first()

        if is_existing_vocab:
            error_text: str = f'У вашій базі вже є словник з назвою "{self.name}".'
            log_text: str = f'Назва "{self.name}" вже використовується в базі.'
            self.add_error_with_log(error_text, log_text)
            return False
        return True

    def check_valid_length(self) -> bool:
        """Перевіряє довжину назви словника"""
        length_filter = LengthFilter(min_length=MIN_LENGTH_VOCAB_NAME, max_length=MAX_LENGTH_VOCAB_NAME)
        if not length_filter.apply(self.name):
            error_text: str = (
                f'Назва словника має містити від {MIN_LENGTH_VOCAB_NAME} до {MAX_LENGTH_VOCAB_NAME} символів.')
            log_text: str = f'Назва "{self.name}" не відповідає вимогам по довжині'
            self.add_error_with_log(error_text, log_text)
            return False
        return True

    def check_valid_characters(self) -> bool:
        """Перевіряє, що назва містить лише дозволені символи"""
        allowed_characters_filter = AllowedCharactersFilter(ALLOWED_CHARACTERS)
        if not allowed_characters_filter.apply(self.name):
            error_text: str = f'Назва може містити лише літери, цифри та символи: "{ALLOWED_CHARACTERS}".'
            log_text: str = f'Назва "{self.name}" містить некоректні символи'
            self.add_error_with_log(error_text, log_text)
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        checks: list[bool] = [self.check_valid_length(),
                              self.check_valid_characters(),
                              self.check_unique_name_per_user()]
        return all(checks)
