from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import VOCAB_PAGINATION_LIMIT
from src.handlers.callback_data import PaginationCallback, VocabCallback


def get_inline_kb_create_vocab(is_with_skip_note: bool = False) -> InlineKeyboardMarkup:
    """Клавіатура з кнопкою скасування при створенні словника"""
    kb = InlineKeyboardBuilder()
    btn_skip_note = InlineKeyboardButton(text='Пропустити',
                                         callback_data='cancel_create_vocab')

    btn_cancel_add = InlineKeyboardButton(text='Скасувати',
                                          callback_data='cancel_create_vocab')

    kb.row(btn_skip_note, btn_cancel_add, width=1) if is_with_skip_note else kb.row(btn_cancel_add)

    return kb.as_markup()


def get_inline_kb_confirm_cancel() -> InlineKeyboardMarkup:
    """Клавіатура для підтвердження або скасування створення словника"""
    kb = InlineKeyboardBuilder()
    btn_agree = InlineKeyboardButton(text='✅ Так',
                                     callback_data=PaginationCallback(name='vocab_base',
                                                                      page=1,
                                                                      limit=VOCAB_PAGINATION_LIMIT).pack())
    btn_cancel = InlineKeyboardButton(text='❌ Ні',
                                      callback_data='create_vocab')
    kb.row(btn_agree, btn_cancel)

    return kb.as_markup()
