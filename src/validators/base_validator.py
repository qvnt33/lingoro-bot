import logging


class ValidatorBase:
    """Базовий клас для загальних перевірок"""

    def __init__(self) -> None:
        self.errors_lst: list = []  # Загальний список для помилок

    def add_error_with_log(self, error_text: str, log_text: str) -> None:
        """Додає помилку та виводить логування"""
        logging.warning(log_text)  # Виведення логу
        self.errors_lst.append(error_text)  # Додавання помилки

    def format_errors(self) -> str:
        """Форматує список помилок у нумерований рядок"""
        formatted_errors_lst: list = []  # Список всіх відформатованих помилок

        for num, error in enumerate(iterable=self.errors_lst, start=1):
            # Форматування кожного рядка з номером і помилкою
            formatted_error: str = f'{num}. {error}'
            formatted_errors_lst.append(formatted_error)

        joined_errors: str = '\n'.join(formatted_errors_lst)
        return joined_errors

    def is_valid(self) -> bool:
        """Перевіряє словникову пару на коректність"""
        return len(self.errors_lst) == 0
