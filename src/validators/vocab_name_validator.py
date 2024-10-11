import sqlalchemy
from .base_validator import ValidatorBase
from sqlalchemy.orm.query import Query

from config import ALLOWED_CHARACTERS, MAX_LENGTH_VOCAB_NAME, MIN_LENGTH_VOCAB_NAME
from db.models import Vocabulary


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
            error_text: str = f'У вашій базі вже є словник з назвою "{self.name}".'
            log_text: str = f'Назва до словника "{self.name}" вже знаходиться у базі користувача'
            self.add_error_with_log(error_text, log_text)
            return False
        return True

    def check_valid_length(self) -> bool:
        """Перевіряє, що коректна довжини"""
        length_name: int = len(self.name)
        if not MIN_LENGTH_VOCAB_NAME <= length_name <= MAX_LENGTH_VOCAB_NAME:
            error_text: str = 'Назва словника має містити від {min_length} до {max_length} символів.'.format(min_length=MIN_LENGTH_VOCAB_NAME,
                                                                                                       max_length=MAX_LENGTH_VOCAB_NAME)
            log_text: str = 'Назва до словника "{vocab_name}" не відповідає вимогам по довжині: довжина {current_length} символів. Допустима довжина: від {min_length} до {max_length}'.format(
                vocab_name=self.name,
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
            error_text: str = 'Назва словника може містити лише літери, цифри та "{allowed_characters}"'.format(
                allowed_characters=ALLOWED_CHARACTERS)
            log_text: str = 'Назва до словника "{vocab_name}" містить некоректні символи. Допустимі символи: літери, цифри та "{allowed_characters}"'.format(
                vocab_name=self.name,
                allowed_characters=ALLOWED_CHARACTERS)
            self.add_error_with_log(error_text, log_text)
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        checks: list[bool] = [self.check_valid_length(),
                              self.check_valid_characters(),
                              self.check_unique_name_per_user()]
        return all(checks)
