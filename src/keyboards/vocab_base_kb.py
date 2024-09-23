import sqlalchemy
from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.database import Session
from db.models import WordPair


def get_inline_kb_user_vocabs(user_vocabs: sqlalchemy.orm.query.Query) -> InlineKeyboardMarkup:
    """Повертає клавіатуру з словниками користувача"""
    inline_builder = InlineKeyboardBuilder()

    btn_menu = InlineKeyboardButton(text='Головне меню',
                                    callback_data='menu')
    btn_vocab_add = InlineKeyboardButton(text='Додати словник',
                                        callback_data='vocab_add')

    # Флаг, чи порожня база словників користувача
    is_vocab_base_empty: bool = len(user_vocabs.all()) == 0

    if not is_vocab_base_empty:
        with Session() as db:
            wordpair_count: str = len(user_vocabs.all())  # Кількість словникових пар в словнику

            for num, item in enumerate(iterable=user_vocabs,
                                       start=1):
                vocab_name: str = item.name  # Назва словника
                # Кількість словникових пар у словнику
                wordpair_count = db.query(WordPair).filter(WordPair.vocabulary_id == item.id).count()

                btn_text: str = f'{vocab_name} [{wordpair_count}]'  # Текст кнопки

                inline_builder.button(text=btn_text,
                                      callback_data=f'vocab_id_{num}')

    inline_builder.adjust(1)  # Кількість кнопок у рядку
    inline_builder.row(btn_vocab_add, btn_menu, width=2)

    return inline_builder.as_markup()
