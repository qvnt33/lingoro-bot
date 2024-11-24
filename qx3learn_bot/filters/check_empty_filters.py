from typing import Iterable

from qx3learn_bot.filters.base_filter import BaseFilter


class CheckEmptyFilter(BaseFilter):
    """Фільтр для перевірки, що значення є порожнім або None"""

    def apply(self, value: Iterable | None) -> bool:
        if value is None:
            is_valid = True
        else:
            is_valid: bool = len(value) == 0
        return is_valid
