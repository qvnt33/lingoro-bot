import logging

import sqlalchemy
from sqlalchemy.orm.query import Query

from db.models import Vocabulary


class VocabNameValidator:
    def __init__(self,
                 name: str,
                 user_id: int,
                 min_len: int,
                 max_len: int,
                 db_session: sqlalchemy.orm.session.Session) -> None:
        self.name: str = name  # Назва словника
        self.user_id: int = user_id  # ID користувача
        self.min_len: int = min_len  # Мінімальна кількість символів для назви словника
        self.max_len: int = max_len  # Максимальна кількість символів для назви словника
        self.db_session: sqlalchemy.orm.session.Session = db_session  # БД сесія
        self.correct_symbols = '-_ '  # Символи які дозволені у назві словника
        self.errors_lst: list = []  # Список помилок назви словника

    def unique_name_per_user(self) -> bool:
        """Перевіряє, що назва словника унікальна серед словників користувача (незалежно від регістру)"""
        is_existing_vocab: Query[Vocabulary] | None = self.db_session.query(Vocabulary).filter(
            Vocabulary.name.ilike(self.name),
            Vocabulary.user_id == self.user_id).first()

        # Якщо у базі вже є словник з такою назвою
        if is_existing_vocab:
            logging.warning(f'Помилка! У базі словників користувача, вже є назва "{self.name}".')

            error_text: str = f'У Вашій базі вже є словник з назвою "{self.name}".'
            self._add_error(error_text)  # Додавання помилки
            return False
        return True

    def valid_all_characters(self) -> bool:
        """Перевіряє, що назва містить лише дозволені символи: літери, цифри, пробіли, тире та підкреслення"""
        # Якщо у назві словника є заборонені символи
        if not all(char.isalnum() or char in self.correct_symbols for char in self.name):
            logging.warning(f'Помилка! Назва словника "{self.name}" містить некоректні символи.')

            error_text: str = 'Назва словника може містити лише літери, цифри, пробіли, тире (-) та підкреслення (_).'
            self._add_error(error_text)  # Додавання помилки
            return False
        return True

    def correct_name_length(self) -> bool:
        """Перевіряє, що довжина назви коректна"""
        current_len: int = len(self.name)  # Кількість символів у назві словника
        if not (self.min_len <= current_len <= self.max_len):
            logging.warning(f'Помилка! Назва словника "{self.name}" має містити від {self.min_len} до {self.max_len} символів.')

            self._add_error(f'Назва словника має містити від "{self.min_len}" до "{self.max_len}" символів.')
            return False
        return True

    def _add_error(self, error_text: str) -> None:
        """Додає помилку до списку помилок"""
        self.errors_lst.append(error_text)

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        self.errors_lst = []  # Очищення списку помилок перед перевіркою

        checks: list[bool] = [self.correct_name_length(),
                              self.valid_all_characters(),
                              self.unique_name_per_user()]
        return all(checks)

    def format_errors(self) -> str:
        """Форматує список помилок у нумерований рядок"""
        formatted_errors_lst: list = []  # Список всіх відформатованих помилок

        for num, error in enumerate(self.errors_lst, start=1):
            # Форматування кожного рядка з номером і помилкою
            formatted_error: str = f'{num}. {error}'
            formatted_errors_lst.append(formatted_error)

        return '\n'.join(formatted_errors_lst)
