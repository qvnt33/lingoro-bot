class ValidatorBase:
    """Базовий клас для загальних перевірок"""

    def __init__(self, errors_lst: list = None) -> None:
        # Спільний список помилок, якщо він переданий
        if errors_lst is None:
            self.errors_lst: list = []
        else:
            self.errors_lst: list = errors_lst

    def add_validator_error(self, error_text: str) -> None:
        """Додає помилку валідатора до бази"""
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
