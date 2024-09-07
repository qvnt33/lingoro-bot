from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton


def get_inline_kb_help() -> InlineKeyboardMarkup:
    """Повертає клавіатуру зі словниками користувача.
    З кнопкою додавання словника чи без неї.
    """
    inline_builder = InlineKeyboardBuilder()

    btn_menu = InlineKeyboardButton(text='Главное меню',
                                    callback_data='menu')

    inline_builder.row(btn_menu)

    return inline_builder.as_markup()
