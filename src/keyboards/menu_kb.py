from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup


def get_kb_menu() -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='📚 Словниковий тренажер', callback_data='vocab_trainer')],
        [InlineKeyboardButton(text='📊 База словників', callback_data='vocab_base')],
        [InlineKeyboardButton(text='⁉️ Довідка', callback_data='help')]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
