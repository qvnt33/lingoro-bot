from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_inline_kb_all_training() -> InlineKeyboardMarkup:
    """Клавіатура з списком словникових тренувань"""
    inline_builder = InlineKeyboardBuilder()

    btn_direct_translation = InlineKeyboardButton(text='Прямий переклад (Word → Translation)',
                                                  callback_data='direct_translation')
    btn_reverse_translation = InlineKeyboardButton(text='Зворотній переклад (Translation → Word)',
                                                   callback_data='reverse_translation')
    btn_change_vocab = InlineKeyboardButton(text='Змінити словник',
                                            callback_data='vocab_trainer')
    btn_menu = InlineKeyboardButton(text='Головне меню',
                                    callback_data='menu')

    inline_builder.row(btn_direct_translation,
                       btn_reverse_translation,
                       btn_change_vocab,
                       btn_menu,
                       width=1)

    return inline_builder.as_markup()


def get_inline_kb_process_training() -> InlineKeyboardMarkup:
    """Клавіатура з списком словникових тренувань"""
    inline_builder = InlineKeyboardBuilder()

    btn_cancel = InlineKeyboardButton(text='Скасувати',
                                      callback_data='cancel_training')

    inline_builder.row(btn_cancel)

    return inline_builder.as_markup()


def get_inline_kb_vocab_selection_training(all_vocabs_data: list[dict],
                                  callback_prefix: str,
                                  is_with_btn_vocab_base: bool = False) -> InlineKeyboardMarkup:
    """Клавіатура з вибором словників.

    Args:
        all_vocabs_data (list[dict]): Список словників зі всіма даними.
        callback_prefix (str): Префікс для callback_data кнопок, залежить від контексту.
        is_for_training (bool): Додавання кнопки "База словників" для розділу "Тренування" та кнопки
        "Додати словник" для розділу "База словників"

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

    if is_with_btn_vocab_base:
        btn_vocab_base = InlineKeyboardButton(text='База словників', callback_data='vocab_base')
        kb.add(btn_vocab_base)

    btn_menu = InlineKeyboardButton(text='Головне меню', callback_data='menu')
    kb.add(btn_menu)

    kb.adjust(1)
    return kb.as_markup()
