from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup


def get_kb_create_vocab_name(is_keep_old_vocab_name: bool = False) -> InlineKeyboardMarkup:
    """Повертає клавіатуру для процесу створення назви словника.
    З флагом, чи додавати кнопку "Залишити поточну назву".
    """
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='Скасувати', callback_data='cancel_create_vocab')]]

    if is_keep_old_vocab_name:
        btn_keep_old_vocab_name: list[InlineKeyboardButton] = [
            InlineKeyboardButton(text='Залишити поточну назву', callback_data='keep_old_vocab_name')]
        buttons.insert(0, btn_keep_old_vocab_name)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_kb_create_vocab_description() -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='Пропустити', callback_data='skip_create_vocab_description')],
        [InlineKeyboardButton(text='Змінити назву словника', callback_data='change_vocab_name')],
        [InlineKeyboardButton(text='Скасувати', callback_data='cancel_create_vocab')]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_kb_create_wordpairs(is_with_btn_status: bool = True) -> InlineKeyboardMarkup:
    """Повертає клавіатуру для процесу додавання словникових пар"""
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='Зберегти', callback_data='save_vocab')],
        [InlineKeyboardButton(text='Скасувати', callback_data='cancel_create_vocab')]]

    if is_with_btn_status:
        btn_status: list[InlineKeyboardButton] = [
            InlineKeyboardButton(text='Статус', callback_data='create_wordpairs_status')]
        buttons.insert(1, btn_status)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_kb_confirm_cancel() -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text='✅ Так', callback_data='vocab_base')],
        [InlineKeyboardButton(text='❌ Ні', callback_data='cancel_create_vocab_no')]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
