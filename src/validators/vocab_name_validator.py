import sqlalchemy
from .base_validator import ValidatorBase
from sqlalchemy.orm.query import Query

from config import ALLOWED_CHARACTERS, MAX_LENGTH_VOCAB_NAME, MIN_LENGTH_VOCAB_NAME
from db.models import Vocabulary
from tools.read_data import app_data


class VocabNameValidator(ValidatorBase):
    def __init__(self,
                 name: str,
                 user_id: int,
                 db_session: sqlalchemy.orm.session.Session) -> None:
        super().__init__()  # Виклик конструктора базового класу
        self.name: str = name  # Назва словника
        self.user_id: int = user_id  # ID користувача
        self.db_session: sqlalchemy.orm.session.Session = db_session  # БД сесія

    def check_unique_name_per_user(self) -> bool:
        """Перевіряє, що назва словника унікальна серед словників користувача (незалежно від регістру)"""
        is_existing_vocab: Query[Vocabulary] | None = self.db_session.query(Vocabulary).filter(
            Vocabulary.name.ilike(self.name),
            Vocabulary.user_id == self.user_id).first()

        # Якщо у базі вже є словник з такою назвою
        if is_existing_vocab:
            error_text: str = app_data['errors']['vocab']['name']['name_exists'].format(name=self.name)
            log_text: str = app_data['logging']['warning']['vocab']['name']['name_exists'].format(name=self.name)
            self.add_error_with_log(error_text, log_text)
            return False
        return True

    def check_valid_length(self, name: str, min_len: int, max_len: int) -> bool:
        """Перевіряє, що коректна довжини"""
        length_name: int = len(name)
        if not min_len <= length_name <= max_len:
            error_text: str = app_data['errors']['vocab']['name']['invalid_length'].format(
                min_length=MIN_LENGTH_VOCAB_NAME,
                max_length=MAX_LENGTH_VOCAB_NAME)
            log_text: str = app_data['logging']['warning']['vocab']['name']['invalid_length'].format(
                name=self.name,
                current_length=length_name,
                min_length=MIN_LENGTH_VOCAB_NAME,
                max_length=MAX_LENGTH_VOCAB_NAME)
            self.add_error_with_log(error_text, log_text)
            return False
        return True

    def check_valid_characters(self) -> bool:
        """Перевіряє, що містить лише коректні символи"""
        # Якщо у назві словника є заборонені символи
        if not all(char.isalnum() or char in ALLOWED_CHARACTERS for char in self.name):
            error_text: str = app_data['errors']['vocab']['name']['invalid_characters'].format(
                allowed_characters=ALLOWED_CHARACTERS)
            log_text: str = app_data['logging']['warning']['vocab']['name']['invalid_characters'].format(
                name=self.name,
                allowed_characters=ALLOWED_CHARACTERS)
            self.add_error_with_log(error_text, log_text)
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        checks: list[bool] = [self.check_valid_length(self.name, MIN_LENGTH_VOCAB_NAME, MAX_LENGTH_VOCAB_NAME),
                              self.check_valid_characters(),
                              self.check_unique_name_per_user()]
        return all(checks)
