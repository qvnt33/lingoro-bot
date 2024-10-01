from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import VOCAB_PAGINATION_LIMIT
from src.handlers.callback_data import PaginationCallback, VocabCallback


def get_inline_kb_vocab_base(vocab_lst: list,
                             start_offset: int,
                             end_offset: int,
                             current_page: int,
                             total_pages_pagination: int,
                             limit: int,
                             is_vocab_base_empty: bool) -> InlineKeyboardMarkup:
    """Клавіатура з кнопками для вибору словників та пагінації"""
    kb = InlineKeyboardBuilder()

    # Якщо у словнику є словникові пари
    if not is_vocab_base_empty:
        # Додавання кнопок словників для поточної сторінки
        for vocab in vocab_lst[start_offset:end_offset]:
            total_wordpairs: int = len(vocab['wordpairs'])  # Кількість словникових пар у словнику
            vocab_button_text: str = f'{vocab['name']} [{total_wordpairs}]'
            kb.button(text=vocab_button_text, callback_data=VocabCallback(vocab_id=vocab['id']).pack())

        kb.adjust(1)

        # Додавання пагінації, якщо сторінок більше 1
        if total_pages_pagination > 1:
            btn_prev_page = InlineKeyboardButton(
                text='⬅️',
                callback_data=PaginationCallback(name='vocab_base', page=current_page - 1, limit=limit).pack())
            btn_page_info = InlineKeyboardButton(
                text=f'{current_page}/{total_pages_pagination}',
                callback_data='neutral_call')
            btn_next_page = InlineKeyboardButton(
                text='➡️',
                callback_data=PaginationCallback(name='vocab_base', page=current_page + 1, limit=limit).pack())

            kb.row(btn_prev_page, btn_page_info, btn_next_page, width=3)

    btn_add_vocab = InlineKeyboardButton(
        text='➕ Створити словник',
        callback_data='create_vocab')

    btn_menu = InlineKeyboardButton(
        text='🏠 Головне меню',
        callback_data='menu')

    kb.row(btn_add_vocab, btn_menu, width=1)

    return kb.as_markup()


def get_inline_kb_add_vocab() -> InlineKeyboardMarkup:
    """Клавіатура з кнопкою скасування при створенні словника"""
    kb = InlineKeyboardBuilder()
    btn_cancel_add = InlineKeyboardButton(text='Скасувати',
                                          callback_data=PaginationCallback(name='vocab_base',
                                                                           page=1,
                                                                           limit=VOCAB_PAGINATION_LIMIT).pack())
    kb.row(btn_cancel_add)
    return kb.as_markup()
