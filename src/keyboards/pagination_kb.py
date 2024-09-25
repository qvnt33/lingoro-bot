from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_inline_kb_pagination(current_page, max_page, chunks) -> InlineKeyboardMarkup:
    """Повертає клавіатуру з кнопками головного меню"""
    inline_builder = InlineKeyboardBuilder()

    for i in chuncks:

    btn_left = InlineKeyboardButton(text='←',
                                    callback_data=f'to-left-{max_page}')
    btn_page = InlineKeyboardButton(text=f'{current_page + 1}/{max_page}',
                                    callback_data='count')
    btn_right = InlineKeyboardButton(text='→',
                                    callback_data=f'to-right-{max_page}')
    btn_other = InlineKeyboardButton(text='Поменять город',
                                     callback_data='choose_city')

    inline_builder.row(btn_left,
                       btn_page,
                       btn_right,
                       btn_other,
                       width=3)

    return inline_builder.as_markup()
