import logging

import sqlalchemy
from sqlalchemy.orm.query import Query

from db.models import Vocabulary
from tools.escape_markdown import escape_markdown
from tools.read_data import app_data


class VocabNameValidator:
    def __init__(self,
                 vocab_name: str,
                 user_id: int,
                 min_length_name: int,
                 max_length_name: int,
                 db: sqlalchemy.orm.session.Session) -> None:
        self.vocab_name: str = vocab_name  # Назва словника
        self.user_id: int = user_id  # ID користувача
        self.min_length_name: int = min_length_name  # Мінімальна кількість символів для назви словника
        self.max_length_name: int = max_length_name  # Максимальна кількість символів для назви словника
        self.db: sqlalchemy.orm.session.Session = db  # Database
        self.errors_lst: list = []  # Список помилок назви словника

    def _add_error(self, error_text: str) -> None:
        """Додає помилку до списку помилок"""
        self.errors_lst.append(error_text)

    def unique_vocab_name_per_user(self) -> bool:
        """Перевіряє, що назва словника унікальна серед словників користувача (незалежно від регістру)"""
        is_existing_vocab: Query[Vocabulary] | None = self.db.query(Vocabulary).filter(
            Vocabulary.name.ilike(self.vocab_name),
            Vocabulary.user_id == self.user_id).first()

        # Якщо у базі вже є словник з такою назвою
        if is_existing_vocab:
            self._add_error(f'У базі словників вже є словник з назвою "{escape_markdown(self.vocab_name)}".')

            logging.warning(f'Помилка! У базі словників користувача, вже є словник введеною назвою')
            return False
        return True

    def valid_all_characters(self) -> bool:
        """Перевіряє, що назва містить лише дозволені символи: літери, цифри, пробіли, тире та підкреслення"""
        # Якщо у назві словника є заборонені символи
        if not all(char.isalnum() or char in '-_ ' for char in self.vocab_name):
            self._add_error(f'Назва словника має містити лише *літери*, *цифри*, *пробіли*, *тире* та *підкреслення*.')

            logging.warning(f'Помилка! Назва словника містить некоректні символи.')
            return False
        return True

    def correct_name_length(self) -> bool:
        """Перевіряє, що довжина назви коректна"""
        length_name: int = len(self.vocab_name)
        if not (self.min_length_name <= length_name <= self.max_length_name):
            self._add_error(f'Назва словника має містити від "{self.min_length_name}" до "{self.max_length_name}" символів.')

            logging.warning(f'Помилка! Введена назва словника, містить некоректну кількість символів "{length_name}". Має містити  від "{self.min_length_name}"  до "{self.max_length_name}".')
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        self.errors_lst = []  # Очищуємо помилки перед перевіркою
        checks: list[bool] = [self.correct_name_length(),
                              self.valid_all_characters(),
                              self.unique_vocab_name_per_user()]
        return all(checks)

    def format_errors(self) -> str:
        """Форматує список помилок у нумерований рядок"""
        formatted_errors_lst: list = []  # Список всіх відформатованих помилок

        for num, error in enumerate(self.errors_lst, start=1):
            # Форматування кожного рядка з номером і помилкою
            formatted_error: str = f'*{num}*. {escape_markdown(error)}'
            formatted_errors_lst.append(formatted_error)

        return '\n'.join(formatted_errors_lst)
