import sqlalchemy
from sqlalchemy.orm.query import Query

from db.models import Vocabulary
from tools.read_data import app_data


class VocabNameValidator:
    def __init__(self, name: str,
                 min_length: int,
                 max_length: int,
                 db: sqlalchemy.orm.session.Session) -> None:
        self.name: str = name
        self.errors: list = []
        self.min_length_vocab_name: int = min_length
        self.max_length_vocab_name: int = max_length
        self.db: sqlalchemy.orm.session.Session = db

    def _add_error(self, error_text: str) -> None:
        """Додає помилку до списку"""
        self.errors.append(error_text)

    def unique_vocab_name_per_user(self, user_id: int) -> bool:
        """Перевіряє, що назва унікальна серед словників користувача (незалежно від регістру)"""
        existing_vocab: Query[Vocabulary] | None = self.db.query(Vocabulary).filter(
            Vocabulary.name.ilike(self.name),
            Vocabulary.user_id == user_id).first()

        if existing_vocab:
            self._add_error(app_data['create_vocab']['name']['errors']['existing_vocab'])
            return False
        return True

    def valid_all_characters(self) -> bool:
        """Перевіряє, що назва містить лише дозволені символи: літери, цифри, пробіли, тире та підкреслення"""
        if not all(char.isalnum() or char in '-_ ' for char in self.name):
            self._add_error(app_data['create_vocab']['name']['errors']['invalid_characters'])
            return False
        return True

    def correct_length(self) -> bool:
        """Перевіряє, що довжина коректна назви"""
        if not (self.min_length_vocab_name <= len(self.name) <= self.max_length_vocab_name):
            self._add_error(app_data['create_vocab']['name']['errors']['incorrect_length']
                            .format(self.min_length_vocab_name,
                                    self.max_length_vocab_name))
            return False
        return True

    def is_valid(self, user_id: int) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        self.errors = []  # Очищуємо помилки перед перевіркою
        checks: list[bool] = [self.correct_length(),
                              self.valid_all_characters(),
                              self.unique_vocab_name_per_user(user_id)]
        return all(checks)

    def format_errors(self) -> str:
        """Форматує список помилок у нумерований рядок"""
        return '\n'.join([f'{num}. {error}' for num, error in enumerate(self.errors, start=1)])
