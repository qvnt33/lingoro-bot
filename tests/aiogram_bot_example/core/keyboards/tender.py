from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.callback_data import TenderCall, PaginationCall


class TenderKB:
    @staticmethod
    def confirm_add_tender(user_id: int, tender_id: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text="❇️ Добавить", callback_data=TenderCall(action="accept", tender_id=tender_id, cr_user_id=user_id))
        kb.button(text="❌ Отменить", callback_data=TenderCall(action="cancel", tender_id=tender_id, cr_user_id=user_id))
        return kb.as_markup()

    @staticmethod
    def pagination(command, max_page: int, current_page: int=0,):
        print(max_page, current_page)
        kb = InlineKeyboardBuilder()
        if current_page > 0:
            kb.button(text="⬅️", callback_data=PaginationCall(command=command, page=current_page-1))
        if max_page-1 > current_page:
            kb.button(text="➡️", callback_data=PaginationCall(command=command, page=current_page+1))
        return kb.as_markup()