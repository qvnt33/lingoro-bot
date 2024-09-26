from aiogram.filters.callback_data import CallbackData


class VocabCallback(CallbackData, prefix='vocab'):
    vocab_id: int


class PaginationCallback(CallbackData, prefix='pagination'):
    name: str  # Ім'я
    page: int  # Номер сторінки
    limit: int  # Ліміт словників на сторінці
