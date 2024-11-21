from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_kb_vocab_options() -> InlineKeyboardMarkup:
    """Клавіатура з кнопками головного меню"""
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='Видалити словник', callback_data='delete_vocab')],
        [InlineKeyboardButton(text='Назад', callback_data='vocab_base')],
        [InlineKeyboardButton(text='Головне меню', callback_data='menu')]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_kb_confirm_delete() -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='✅ Так', callback_data='accept_delete_vocab')],
        [InlineKeyboardButton(text='❌ Ні', callback_data='vocab_base')]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_kb_accept_delete_vocab() -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='База словників', callback_data='vocab_base')],
        [InlineKeyboardButton(text='Головне меню', callback_data='menu')]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_kb_vocab_selection_base(all_vocabs_data: list[dict]) -> InlineKeyboardMarkup:
    """Повертає клавіатуру з вибором словників для розділу "База словників".

    Notes:
        Порядок словників обертається.

    Args:
        all_vocabs_data (list[dict]): Список словників зі всіма даними.

    Returns:
        InlineKeyboardMarkup: Сформована клавіатура.
    """
    kb = InlineKeyboardBuilder()

    # Генерація кнопок для кожного словника
    for vocab in all_vocabs_data[::-1]:
        vocab_id: int = vocab.get('id')
        vocab_name: str = vocab.get('name')
        wordpairs_count: int = vocab.get('wordpairs_count')

        btn_text: str = f'{vocab_name} [{wordpairs_count}]'
        callback_data_text: str = f'select_vocab_base_{vocab_id}'

        btn_vocab = InlineKeyboardButton(text=btn_text, callback_data=callback_data_text)
        kb.add(btn_vocab)

    btn_create_vocab = InlineKeyboardButton(text='Додати словник', callback_data='create_vocab')
    btn_menu = InlineKeyboardButton(text='Головне меню', callback_data='menu')
    kb.add(btn_create_vocab, btn_menu)

    kb.adjust(1)
    return kb.as_markup()
