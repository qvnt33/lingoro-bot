import logging

from tools.read_data import app_data


class VocabNoteValidator:
    def __init__(self,
                 note: str,
                 vocab_name: str,
                 min_len: int,
                 max_len: int) -> None:
        self.note: str = note  # Примітка до словника
        self.vocab_name: str = vocab_name  # Назва словника
        self.min_len: int = min_len  # Мінімальна к-сть символів у примітки до словника
        self.max_len: int = max_len  # Максимальна к-сть символів у примітки до словника
        self.errors_lst: list = []  # Список усіх помилок

    def _add_error(self, error_text: str) -> None:
        """Додає помилку до списку помилок"""
        self.errors_lst.append(error_text)

    def correct_length(self) -> bool:
        """Перевіряє, що коректна к-сть символів у примітці до словника"""
        current_length: int = len(self.note)  # К-сть символів у примітці

        # Коректна кількість символів у примітці
        is_valid_length: bool = self.min_len <= current_length <= self.max_len

        # Якщо к-сть некоректна
        if not is_valid_length:
            logging.warning(f'Некоректна кількість символів у примітці до словника: "{self.vocab_name}."'
                f'Очікується від {self.min_len} до {self.max_len} символів.')

            error_text: str = app_data['errors']['vocab']['note']['invalid_length'].format(min_len=self.min_len,
                                                                                           max_len=self.max_len)
            self._add_error(error_text)  # Додавання помилки
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        self.errors_lst = []  # Очищення списку помилок перед перевіркою

        checks: list[bool] = [self.correct_length()]
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
