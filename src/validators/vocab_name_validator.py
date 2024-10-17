import logging

import sqlalchemy
from .base_validator import ValidatorBase
from sqlalchemy.orm.query import Query

from config import ALLOWED_CHARACTERS, MAX_LENGTH_VOCAB_NAME, MIN_LENGTH_VOCAB_NAME
from db.models import Vocabulary
from src.filters.allowed_chars_filter import AllowedCharactersFilter
from src.filters.length_filter import LengthFilter


class VocabNameValidator(ValidatorBase):
    def __init__(self,
                 name: str,
                 user_id: int,
                 db_session: sqlalchemy.orm.session.Session,
                 errors_lst: list = None) -> None:
        super().__init__(errors_lst)

        self.name: str = name  # Назва словника
        self.user_id: int = user_id  # ID користувача
        self.db_session: sqlalchemy.orm.session.Session = db_session  # БД сесія

        # Фільтри
        self.allowed_character_filter = AllowedCharactersFilter(ALLOWED_CHARACTERS)
        self.length_filter = LengthFilter(min_length=MIN_LENGTH_VOCAB_NAME, max_length=MAX_LENGTH_VOCAB_NAME)

    def check_unique_name_per_user(self) -> bool:
        """Перевіряє, що назва словника унікальна серед словників користувача (незалежно від регістру)"""
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "Назва словника унікальна серед словників користувача"')

        is_existing_vocab: Query[Vocabulary] | None = self.db_session.query(Vocabulary).filter(
            Vocabulary.name.ilike(self.name),
            Vocabulary.user_id == self.user_id).first()

        if is_existing_vocab:
            logging.warning(f'Назва словника "{self.name}" вже використовується в базі словників')
            self.add_validator_error(f'У вашій базі словників вже є словник з назвою "{self.name}".')
            return False
        return True

    def check_valid_length(self) -> bool:
        """Перевіряє, що довжина назви словника коректна"""
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "Довжина назви словника коректна"')

        is_valid_length: bool = self.length_filter.apply(self.name)  # Чи коректна довжина

        if not is_valid_length:
            logging.warning(f'Некоректна кількість символів у назві словника "{self.name}"')
            self.add_validator_error(
                f'Довжина назви словника має бути від {MIN_LENGTH_VOCAB_NAME} до {MAX_LENGTH_VOCAB_NAME} символів.')
            return False
        return True

    def check_valid_characters(self) -> bool:
        """Перевіряє, що назва містить лише дозволені символи"""
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "Назва словника містить лише дозволені символі"')

        is_valid_allowed_chars: bool = self.allowed_character_filter.apply(self.name)  # Чи коректні символи
        if not is_valid_allowed_chars:
            logging.warning(f'Назва словника може містити лише літери, цифри та символи: "{ALLOWED_CHARACTERS}"')
            self.add_validator_error(
                f'Назва словника може містити лише літери, цифри та символи: "{ALLOWED_CHARACTERS}".')
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        is_valid_flag = True

        if self.check_valid_length():
            logging.info('ПЕРЕВІРКА ПРОЙДЕНА: "Довжина назви словника коректна"')
        else:
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "Довжина назви словника коректна"')
            is_valid_flag = False

        if self.check_valid_characters():
            logging.info('ПЕРЕВІРКА ПРОЙДЕНА: "Назва словника містить лише дозволені символі"')
        else:
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "Назва словника містить лише дозволені символі"')
            is_valid_flag = False

        if self.check_unique_name_per_user():
            logging.info('ПЕРЕВІРКА ПРОЙДЕНА: "Назва словника унікальна серед словників користувача"')
        else:
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "Назва словника унікальна серед словників користувача"')
            is_valid_flag = False

        logging.info('ПЕРЕВІРКА НАЗВИ СЛОВНИКА УСПІШНО ПРОЙДЕНА')
        return is_valid_flag
