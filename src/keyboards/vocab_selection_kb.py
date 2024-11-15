from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_inline_kb_vocab_selection(all_vocabs_data: list[dict],
                                  callback_prefix: str,
                                  is_with_btn_create_vocab: bool = True) -> InlineKeyboardMarkup:
    """Клавіатура з вибором словників.

    Args:
        all_vocabs_data (list[dict]): Список словників зі всіма даними.
        callback_prefix (str): Префікс для callback_data кнопок, залежить від контексту.
        is_with_btn_create_vocab (bool): Додати кнопку "Додати словник", якщо True.

    Returns:
        InlineKeyboardMarkup: Сформована клавіатура.
    """
    kb = InlineKeyboardBuilder()

    # Генерація кнопок для кожного словника
    for vocab in all_vocabs_data[::-1]:
        vocab_id: int = vocab['id']
        vocab_name: str = vocab['name']
        wordpairs_count: int = vocab['wordpairs_count']

        btn_text: str = f'{vocab_name} [{wordpairs_count}]'
        callback_data_text: str = f'{callback_prefix}_{vocab_id}'

        btn_vocab = InlineKeyboardButton(text=btn_text, callback_data=callback_data_text)
        kb.add(btn_vocab)

    # Додаємо кнопку додавання нового словника та кнопку виходу
    if is_with_btn_create_vocab:
        btn_create_vocab = InlineKeyboardButton(text='Додати словник', callback_data='create_vocab')
        kb.add(btn_create_vocab)

    btn_menu = InlineKeyboardButton(text='Головне меню', callback_data='menu')
    kb.add(btn_menu)

    kb.adjust(1)
    return kb.as_markup()


def get_inline_kb_vocab_options() -> InlineKeyboardMarkup:
    """Клавіатура з кнопками головного меню"""
    kb = InlineKeyboardBuilder()

    btn_delete_vocab = InlineKeyboardButton(text='Видалити словник', callback_data='delete_vocab')
    btn_to_back = InlineKeyboardButton(text='Назад', callback_data='vocab_base')
    btn_menu = InlineKeyboardButton(text='Головне меню', callback_data='menu')

    kb.row(btn_delete_vocab,
                       btn_to_back,
                       btn_menu,
                       width=1)

    return kb.as_markup()
