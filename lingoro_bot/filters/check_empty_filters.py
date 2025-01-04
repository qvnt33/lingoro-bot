from collections.abc import Sized

from lingoro_bot.filters.base_filter import BaseFilter


class CheckEmptyFilter(BaseFilter):
    """Фільтр для перевірки, що значення є порожнім або None"""

    def apply(self, value: Sized | None) -> bool:
        is_valid: bool = value is None or len(value) == 0
        return is_valid
