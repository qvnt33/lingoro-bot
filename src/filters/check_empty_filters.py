from typing import Iterable

from .base_filter import BaseFilter


class CheckEmptyFilter(BaseFilter):
    """Фільтр для перевірки, що значення пусте"""

    def apply(self, value: Iterable | None) -> bool:
        if value is None:
            is_valid = True
        else:
            current_length: int = len(value)
            is_valid: bool = current_length == 0
        return is_valid
