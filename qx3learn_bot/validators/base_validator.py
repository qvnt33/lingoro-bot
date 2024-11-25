class ValidatorBase:
    """Батьківський (базовий) валідатор для інших"""

    def __init__(self, errors: list[str] | None = None) -> None:
        self.errors: list[str] = errors if errors is not None else []

    def add_error(self, error_text: str) -> None:
        """Додає повідомлення про помилку до загального списку помилок"""
        self.errors.append(error_text)

    def format_errors(self) -> str:
        """Форматує список помилок в текст, зʼєднуючи помилки переносом рядка"""
        formatted_errors: list[str] = [f'- {error}' for error in self.errors]
        return '\n'.join(formatted_errors)
