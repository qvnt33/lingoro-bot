import sqlalchemy

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton


def get_inline_kb_dict(user_dicts: sqlalchemy.orm.query.Query,
                       is_with_add_btn: bool = True) -> InlineKeyboardMarkup:
    """Повертає клавіатуру зі словниками користувача.
    З кнопкою "Додати новий словник" чи без неї.
    """
    inline_builder = InlineKeyboardBuilder()

    btn_menu = InlineKeyboardButton(text='Головне меню',
                                    callback_data='menu')
    btn_dict_add = InlineKeyboardButton(text='Додати новий словник',
                                        callback_data='dict_add')

    for num, item in enumerate(iterable=user_dicts,
                               start=1):
        dict_name = item.dictionary_name  # Назва словника
        wordpair_count = item.wordpair_count  # К-сть словникових пар в словнику
        dict_note = item.note  # Примітка до словника
        btn_text = f'{dict_name} [{wordpair_count}]: {dict_note}'  # Текст кнопки

        inline_builder.button(text=btn_text,
                              callback_data=f'calldict_{num}')

    if is_with_add_btn:
        # Додає кнопку додавання словника в залежності від переданого прапорця
        inline_builder.row(btn_dict_add)

    inline_builder.adjust(1)  # К-сть кнопок у рядку
    inline_builder.row(btn_menu)

    return inline_builder.as_markup()
