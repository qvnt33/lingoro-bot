from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_kb_all_training() -> InlineKeyboardMarkup:
    """Клавіатура з списком словникових тренувань"""
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='📖 Прямий переклад (W -> T)', callback_data='direct_translation')],
        [InlineKeyboardButton(text='📖 Зворотній переклад (T -> W)', callback_data='reverse_translation')],
        [InlineKeyboardButton(text='📚 Змінити словник', callback_data='vocab_trainer')],
        [InlineKeyboardButton(text='🏠 Головне меню', callback_data='menu')]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_kb_finish_training() -> InlineKeyboardMarkup:
    """Повертає клавіатуру з функціоналом після завершення тренування"""
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='🔄 Повторити тренування', callback_data='repeat_training')],
        [InlineKeyboardButton(text='🎯 Змінити тип тренування', callback_data='change_training_mode')],
        [InlineKeyboardButton(text='📚 Змінити словник', callback_data='vocab_trainer')],
        [InlineKeyboardButton(text='🏠 Головне меню', callback_data='menu')]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_kb_process_training() -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='➡️ Пропустити', callback_data='skip_word')],
        [
            InlineKeyboardButton(text='💡 Анотація', callback_data='show_annotation'),
            InlineKeyboardButton(text='💬 Переклад', callback_data='show_translation')],
        [InlineKeyboardButton(text='❌ Завершити тренування', callback_data='cancel_training')]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_kb_confirm_cancel_training() -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='✅ Так', callback_data='accept_cancel_training')],
        [InlineKeyboardButton(text='❌ Ні', callback_data='decline_cancel_training')]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_kb_vocab_selection_training(all_vocabs_data: list[dict],
                                    is_with_btn_vocab_base: bool = False) -> InlineKeyboardMarkup:
    """Повертає клавіатуру з вибором словників для розділу "Тренування".

    Args:
        all_vocabs_data (list[dict]): Список словників зі всіма даними.
        is_with_btn_vocab_base (bool): Прапор, чи потрібно додавати кнопку "База словників". За замовчуванням False.
        "Додати словник" для розділу "База словників"

    Returns:
        InlineKeyboardMarkup: Сформована клавіатура.
    """
    kb = InlineKeyboardBuilder()

    # Генерація кнопок для кожного словника
    for vocab in all_vocabs_data:
        vocab_id: int = vocab.get('id')
        vocab_name: str = vocab.get('name')
        wordpairs_count: int = vocab.get('wordpairs_count')

        btn_text: str = f'{vocab_name} [{wordpairs_count}]'
        callback_data_text: str = f'select_vocab_training_{vocab_id}'

        btn_vocab = InlineKeyboardButton(text=btn_text, callback_data=callback_data_text)
        kb.add(btn_vocab)

    if is_with_btn_vocab_base:
        btn_vocab_base = InlineKeyboardButton(text='База словників', callback_data='vocab_base')
        kb.add(btn_vocab_base)

    btn_menu = InlineKeyboardButton(text='Головне меню', callback_data='menu')
    kb.add(btn_menu)

    kb.adjust(1)
    return kb.as_markup()
