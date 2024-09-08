import sqlalchemy

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton


def get_inline_kb_user_vocabs(user_vocabs: sqlalchemy.orm.query.Query,
                             is_with_add_btn: bool = True) -> InlineKeyboardMarkup:
    """Повертає клавіатуру зі словниками користувача.
    З кнопкою "Додати новий словник" чи без неї.
    """
    inline_builder = InlineKeyboardBuilder()

    btn_menu = InlineKeyboardButton(text='Головне меню',
                                    callback_data='menu')
    btn_dict_add = InlineKeyboardButton(text='Додати новий словник',
                                        callback_data='vocab_add')

    for num, item in enumerate(iterable=user_vocabs,
                               start=1):
        vocab_name = item.dictionary_name  # Назва словника
        wordpair_count = item.wordpair_count  # Кількість словникових пар в словнику
        vocab_note = item.note  # Примітка до словника
        btn_text = f'{vocab_name} [{wordpair_count}]: {vocab_note}'  # Текст кнопки

        inline_builder.button(text=btn_text,
                              callback_data=f'vocab_id_{num}')

    if is_with_add_btn:
        # Додає кнопку додавання словника в залежності від переданого прапорця
        inline_builder.row(btn_dict_add)

    inline_builder.adjust(1)  # К-сть кнопок у рядку
    inline_builder.row(btn_menu)

    return inline_builder.as_markup()
