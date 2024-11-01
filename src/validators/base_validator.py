class ValidatorBase:
    def __init__(self, errors: list = None) -> None:
        self.errors: list = errors if errors is not None else []

    def add_error(self, error_text: str) -> None:
        """Додає повідомлення про помилку до загального списку помилок"""
        self.errors.append(error_text)

    def format_errors(self) -> str:
        """Форматує список помилок у нумерований рядок"""
        formatted_errors: list[str] = [f'{num}. {error}' for num, error in enumerate(self.errors, start=1)]
        return '\n'.join(formatted_errors)
