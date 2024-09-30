from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import VOCAB_PAGINATION_LIMIT


def get_inline_kb_create_vocab_name(is_keep_old_vocab_name: bool = False) -> InlineKeyboardMarkup:
    """Клавіатура з кнопкою скасування та залишенням поточної назви при створенні словника"""
    kb = InlineKeyboardBuilder()
    btn_keep_old_vocab_name = InlineKeyboardButton(text='Залишити поточну назву',
                                                   callback_data='keep_old_vocab_name')
    btn_cancel = InlineKeyboardButton(text='Скасувати',
                                      callback_data='cancel_from_vocab_name')
    if is_keep_old_vocab_name:
        kb.row(btn_keep_old_vocab_name)
    kb.row(btn_cancel)

    return kb.as_markup()


def get_inline_kb_create_vocab_note() -> InlineKeyboardMarkup:
    """Клавіатура з кнопкою скасування при створенні словника"""
    kb = InlineKeyboardBuilder()
    btn_skip_creation_note = InlineKeyboardButton(text='Пропустити',
                                                  callback_data='skip_creation_note')
    btn_change_vocab_name = InlineKeyboardButton(text='Змінити назву словника',
                                                  callback_data='change_vocab_name')
    btn_cancel = InlineKeyboardButton(text='Скасувати',
                                      callback_data='cancel_from_vocab_note')

    kb.row(btn_skip_creation_note,
           btn_change_vocab_name,
           btn_cancel,
           width=1)

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
