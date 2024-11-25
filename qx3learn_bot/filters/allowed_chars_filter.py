from qx3learn_bot.filters.base_filter import BaseFilter


class AllowedCharsFilter(BaseFilter):
    """Фільтр для перевірки, що всі символи значення коректні (складаються тільки з букв та цифр,
    або входять до дозволених символів)
    """

    def __init__(self, allowed_chars: tuple[str, ...]) -> None:
        self.allowed_chars: tuple[str, ...] = allowed_chars

    def apply(self, value: str) -> bool:
        is_valid: bool = all(char.isalnum() or char in self.allowed_chars for char in value)
        return is_valid
