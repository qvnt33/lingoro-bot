from aiogram.filters.callback_data import CallbackData


class TenderCall(CallbackData, prefix="tender"):
    action: str
    tender_id: str
    cr_user_id: int

class PaginationCall(CallbackData, prefix="tender"):
    command: str
    page: int