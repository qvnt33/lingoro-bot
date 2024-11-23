from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup


def get_kb_help() -> InlineKeyboardMarkup:
    """Повертає клавіатуру для розділу "Справка" з кнопкою головного меню"""
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='🏠 Головне меню', callback_data='menu')]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
