from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_kb_help() -> InlineKeyboardMarkup:
    """Клавіатура з кнопкою головного меню"""
    inline_builder = InlineKeyboardBuilder()

    btn_menu = InlineKeyboardButton(text='Головне меню',
                                    callback_data='menu')

    inline_builder.row(btn_menu)

    return inline_builder.as_markup()
