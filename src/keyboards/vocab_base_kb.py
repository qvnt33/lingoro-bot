import sqlalchemy
from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_inline_kb_user_vocabs(user_vocabs: sqlalchemy.orm.query.Query,
                             is_with_add_btn: bool = True) -> InlineKeyboardMarkup:
    """Повертає клавіатуру з словниками користувача.
    З кнопкою додавання нового словника чи без неї.
    """
    inline_builder = InlineKeyboardBuilder()

    btn_menu = InlineKeyboardButton(text='Головне меню',
                                    callback_data='menu')
    btn_vocab_add = InlineKeyboardButton(text='Додати новий словник',
                                        callback_data='vocab_add')

    for num, item in enumerate(iterable=user_vocabs,
                               start=1):
        vocab_name: str = item.dictionary_name  # Назва словника
        vocab_note: str = item.note  # Примітка до словника
        wordpair_count: str = item.wordpair_count  # Кількість словникових пар в словнику
        btn_text: str = f'{vocab_name} [{wordpair_count}]: {vocab_note}'  # Текст кнопки

        inline_builder.button(text=btn_text,
                              callback_data=f'vocab_id_{num}')

    # Якщо потрібна кнопка додавання нового словника
    if is_with_add_btn:
        inline_builder.row(btn_vocab_add)

    inline_builder.adjust(1)  # Кількість кнопок у рядку
    inline_builder.row(btn_menu)

    return inline_builder.as_markup()
