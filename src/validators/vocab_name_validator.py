import logging

import sqlalchemy
from sqlalchemy.orm.query import Query

from db.models import Vocabulary
from tools.read_data import app_data


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
            logging.warning(f'У базі словників користувача, вже є назва "{self.name}".')

            error_text: str = app_data['errors']['vocab']['name']['name_exists'].format(name=self.name)
            self._add_error(error_text)  # Додавання помилки
            return False
        return True

    def validate_characters(self) -> bool:
        """Перевіряє, що назва містить лише дозволені символи: літери, цифри, пробіли, тире та підкреслення"""
        # Якщо у назві словника є заборонені символи
        if not all(char.isalnum() or char in self.correct_symbols for char in self.name):
            logging.warning(f'Назва словника "{self.name}" містить некоректні символи.')

            error_text: str = app_data['errors']['vocab']['name']['invalid_characters']
            self._add_error(error_text)  # Додавання помилки
            return False
        return True

    def correct_name_length(self) -> bool:
        """Перевіряє, що довжина назви коректна"""
        current_length: int = len(self.name)  # Кількість символів у назві словника

        # Коректна кількість символів у назві словника
        is_valid_length: bool = self.min_len <= current_length <= self.max_len

        # Якщо к-сть некоректна
        if not is_valid_length:
            logging.warning(f'Некоректна кількість символів у назві словника: "{self.name}". '
                f'Очікується від {self.min_len} до {self.max_len} символів.')

            error_text: str = app_data['errors']['vocab']['name']['invalid_length'].format(min_len=self.min_len,
                                                                                           max_len=self.max_len)
            self._add_error(error_text)  # Додавання помилки
            return False
        return True

    def _add_error(self, error_text: str) -> None:
        """Додає помилку до списку помилок"""
        self.errors_lst.append(error_text)

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        self.errors_lst = []  # Очищення списку помилок перед перевіркою

        checks: list[bool] = [self.correct_name_length(),
                              self.validate_characters(),
                              self.unique_name_per_user()]
        return all(checks)

    def format_errors(self) -> str:
        """Форматує список помилок у нумерований рядок"""
        formatted_errors_lst: list = []  # Список всіх відформатованих помилок

        for num, error in enumerate(iterable=self.errors_lst, start=1):
            # Форматування кожного рядка з номером і помилкою
            formatted_error: str = f'{num}. {error}'
            formatted_errors_lst.append(formatted_error)

            joined_errors: str = '\n'.join(formatted_errors_lst)
        return joined_errors
