from .base_filter import BaseFilter


class ValidLengthFilter(BaseFilter):
    """Фільтр для перевірки довжини значення"""

    def __init__(self, min_length: int, max_length: int) -> None:
        self.min_length: int = min_length
        self.max_length: int = max_length

    def apply(self, value: str) -> bool:
        current_length: int = len(value)
        is_valid: bool = self.min_length <= current_length <= self.max_length
        return is_valid
