from .base_filter import BaseFilter


class CountFilter(BaseFilter):
    """Фільтр для перевірки кількості"""

    def __init__(self, min_count: int, max_count: int) -> None:
        self.min_count: int = min_count
        self.max_count: int = max_count

    def apply(self, value: str) -> bool:
        current_count: int = len(value)
        is_valid: bool = self.min_count <= current_count <= self.max_count
        return is_valid
