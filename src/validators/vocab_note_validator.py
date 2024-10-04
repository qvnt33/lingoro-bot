import logging

import sqlalchemy
from sqlalchemy.orm.query import Query

from db.models import Vocabulary
from tools.escape_markdown import escape_markdown
from tools.read_data import app_data


class VocabNoteValidator:
    def __init__(self,
                 note: str,
                 min_length_vocab_note: int,
                 max_length_vocab_note: int) -> None:
        self.note: str = note  # Примітка до словника
        self.min_length_vocab_note: int = min_length_vocab_note  # Мінімальна кількість символів примітки до словника
        self.max_length_vocab_note: int = max_length_vocab_note  # Максимальна кількість символів примітки до словника
        self.errors_lst: list = []  # Список усіх помилок

    def _add_error(self, error_text: str) -> None:
        """Додає помилку до списку помилок"""
        self.errors_lst.append(error_text)

    def correct_length(self) -> bool:
        """Перевіряє, що коректна довжина примітки"""
        length_note: int = len(self.note)
        if not (self.min_length_vocab_note <= length_note <= self.max_length_vocab_note):
            self._add_error(f'Примітка до словника має містити від "{self.min_length_vocab_note}" до "{self.max_length_vocab_note}" символів.')

            logging.warning(f'Помилка! Примітка до словника, містить некоректну кількість символів "{length_note}". Має містити від "{self.min_length_vocab_note}" до "{self.max_length_vocab_note}".')
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        self.errors_lst = []  # Очищуємо помилки перед перевіркою
        checks: list[bool] = [self.correct_length()]
        return all(checks)

    def format_errors(self) -> str:
        """Форматує список помилок у нумерований рядок"""
        formatted_errors_lst: list = []  # Список всіх відформатованих помилок

        for num, error in enumerate(self.errors_lst, start=1):
            # Форматування кожного рядка з номером і помилкою
            formatted_error: str = f'*{num}*. {escape_markdown(error)}'
            formatted_errors_lst.append(formatted_error)

        return '\n'.join(formatted_errors_lst)
