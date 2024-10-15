from .base_filter import BaseFilter


class NotEmptyFilter(BaseFilter):
    """Фільтр для перевірки, що значення не пусте"""

    def apply(self, value: str | None) -> bool:
        if value is None:
            is_valid = False
        else:
            current_length: int = len(value)
            is_valid: bool = current_length > 0
        return is_valid
