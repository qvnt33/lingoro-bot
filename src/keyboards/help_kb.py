from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_inline_kb_help() -> InlineKeyboardMarkup:
    """Повертає клавіатуру з кнопкою головного меню"""
    inline_builder = InlineKeyboardBuilder()

    btn_menu = InlineKeyboardButton(text='Главное меню',
                                    callback_data='menu')

    inline_builder.row(btn_menu)

    return inline_builder.as_markup()
