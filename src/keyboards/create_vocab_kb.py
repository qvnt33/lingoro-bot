from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import VOCAB_PAGINATION_LIMIT
from src.handlers.callback_data import PaginationCallback, VocabCallback


def get_inline_kb_create_vocab_name(keep_old_vocab_name: bool = False) -> InlineKeyboardMarkup:
    """Клавіатура з кнопкою скасування при створенні словника"""
    kb = InlineKeyboardBuilder()
    btn_cancel = InlineKeyboardButton(text='Скасувати',
                                      callback_data='cancel_from_vocab_name')
    btn_keep_old_vocab_name = InlineKeyboardButton(text='Залишити поточну назву',
                                                   callback_data='keep_old_vocab_name')
    kb.row(btn_cancel, btn_keep_old_vocab_name, width=1) if keep_old_vocab_name else kb.row(btn_cancel, width=1)


    return kb.as_markup()


def get_inline_kb_create_vocab_note() -> InlineKeyboardMarkup:
    """Клавіатура з кнопкою скасування при створенні словника"""
    kb = InlineKeyboardBuilder()
    btn_skip_note = InlineKeyboardButton(text='Пропустити',
                                         callback_data='cancel_create_note')
    btn_cancel = InlineKeyboardButton(text='Скасувати',
                                          callback_data='cancel_from_vocab_note')
    btn_back_to_name = InlineKeyboardButton(text='Змінити назву',
                                            callback_data='change_vocab_name')

    kb.row(btn_skip_note, btn_cancel, btn_back_to_name, width=1)

    return kb.as_markup()


def get_inline_kb_create_wordpairs() -> InlineKeyboardMarkup:
    """Клавіатура з кнопкою скасування при створенні словника"""
    kb = InlineKeyboardBuilder()
    btn_status = InlineKeyboardButton(text='Статус',
                                         callback_data='create_wordpairs_status')
    btn_cancel_add = InlineKeyboardButton(text='Скасувати',
                                          callback_data='cancel_from_wordpairs')
    btn_back_to_name = InlineKeyboardButton(text='Зберегти',
                                            callback_data='back_to_vocab_name')

    kb.row(btn_status, btn_cancel_add, btn_back_to_name, width=1)

    return kb.as_markup()
