from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_inline_kb_vocab_buttons(vocabularies: list, is_with_create_vocab: bool = True) -> InlineKeyboardMarkup:
    """Клавіатура з вибором словників"""
    kb = InlineKeyboardBuilder()

    # Кнопки зі словниками
    for vocab in vocabularies:
        button = InlineKeyboardButton(text=vocab.name, callback_data=f'select_vocab_{vocab.id}')
        kb.add(button)

    btn_add_vocab = InlineKeyboardButton(text='Додати словник', callback_data='create_vocab')
    btn_cancel = InlineKeyboardButton(text='Скасувати', callback_data='menu')

    if is_with_create_vocab:
        kb.add(btn_add_vocab)
    kb.add(btn_cancel)

    kb.adjust(1)

    return kb.as_markup()
