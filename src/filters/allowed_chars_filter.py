# /validators/filters/translation_filter.py
from .base_filter import BaseFilter


class AllowedCharactersFilter(BaseFilter):
    """Фільтр для перевірки коректності символів"""

    def __init__(self, allowed_characters: str) -> None:
        self.allowed_characters: int = allowed_characters

    def apply(self, value: str) -> bool:
        is_valid: bool = all(char.isalnum() or char in self.allowed_characters for char in value)
        return is_valid
