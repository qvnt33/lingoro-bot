from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup


def get_inline_kb_vocab_base() -> InlineKeyboardMarkup:
    """Клавіатура з кнопками головного меню"""
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='Видалити словник', callback_data='delete_vocab')],
        [InlineKeyboardButton(text='Назад', callback_data='vocab_base')],
        [InlineKeyboardButton(text='Головне меню', callback_data='menu')]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
