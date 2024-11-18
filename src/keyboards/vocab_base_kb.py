from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup


def get_inline_kb_vocab_base() -> InlineKeyboardMarkup:
    """Клавіатура з кнопками головного меню"""
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='Видалити словник', callback_data='delete_vocab')],
        [InlineKeyboardButton(text='Назад', callback_data='vocab_base')],
        [InlineKeyboardButton(text='Головне меню', callback_data='menu')]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_inline_kb_confirm_delete() -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='✅ Так', callback_data='accept_delete_vocab')],
        [InlineKeyboardButton(text='❌ Ні', callback_data='vocab_base')]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_inline_kb_accept_delete_vocab() -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='База словників', callback_data='vocab_base')],
        [InlineKeyboardButton(text='Головне меню', callback_data='menu')]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
