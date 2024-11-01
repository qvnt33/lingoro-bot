from .base_filter import BaseFilter


class AllowedCharsFilter(BaseFilter):
    """Фільтр для перевірки, щоб всі символи значення були коректні (складалися тільки з букв та цифр,
    або входили до дозволених символів)
    """

    def __init__(self, allowed_chars: list[str]) -> None:
        self.allowed_chars: list[str] = allowed_chars

    def apply(self, value: str) -> bool:
        is_valid: bool = all(char.isalnum() or char in self.allowed_chars for char in value)
        return is_valid
