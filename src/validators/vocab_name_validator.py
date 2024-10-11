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
            error_text: str = f'У вашій базі вже є словник з назвою "{self.name}" (незалежно від регістру).'
            log_text: str = (f'Назва до словника "{self.name}" вже знаходиться у базі користувача'
                             '(незалежно від регістру)')
            self.add_error_with_log(error_text, log_text)  # Додавання помилок та виведення логування
            return False
        return True

    def check_valid_length(self) -> bool:
        """Перевіряє, що коректна довжини"""
        length_vocab_name: int = len(self.name)  # Довжина назви словника
        # Коректна довжина
        is_valid_length: bool = MIN_LENGTH_VOCAB_NAME <= length_vocab_name <= MAX_LENGTH_VOCAB_NAME
        if not is_valid_length:
            error_text: str = (
                f'Назва словника має містити від {MIN_LENGTH_VOCAB_NAME} до {MAX_LENGTH_VOCAB_NAME} символів.')
            log_text: str = (
                f'Назва до словника "{self.name}" не відповідає вимогам по довжині: '
                f'довжина {length_vocab_name} символів. '
                f'Допустима довжина: від {MIN_LENGTH_VOCAB_NAME} до {MAX_LENGTH_VOCAB_NAME}')
            self.add_error_with_log(error_text, log_text)  # Додавання помилок та виведення логування
            return False
        return True

    def check_valid_characters(self) -> bool:
        """Перевіряє, що містить лише коректні символи"""
        # У назві словника всі символи коректні
        is_valid_characters: bool = all(char.isalnum() or char in ALLOWED_CHARACTERS for char in self.name)
        if not is_valid_characters:
            error_text: str = f'Назва словника може містити лише літери, цифри та символи: "{ALLOWED_CHARACTERS}".'
            log_text: str = (
                f'Назва до словника "{self.name}" містить некоректні символи. '
                f'Допустимі символи: літери, цифри та "{ALLOWED_CHARACTERS}"')
            self.add_error_with_log(error_text, log_text)    # Додавання помилок та виведення логування
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        checks: list[bool] = [self.check_valid_length(),
                              self.check_valid_characters(),
                              self.check_unique_name_per_user()]
        return all(checks)
