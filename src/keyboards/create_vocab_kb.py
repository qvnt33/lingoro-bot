from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import VOCAB_PAGINATION_LIMIT
from src.handlers.callback_data import PaginationCallback


def get_kb_create_vocab_name(is_keep_old_vocab_name: bool = False) -> InlineKeyboardMarkup:
    """Повертає клавіатуру з кнопкою скасування процесу створення словника та, за потреби,
    з кнопкою залишення поточної назви словника.
    """
    kb = InlineKeyboardBuilder()

    btn_keep_old_vocab_name = InlineKeyboardButton(text='Залишити поточну назву',
                                                   callback_data='keep_old_vocab_name')
    btn_cancel = InlineKeyboardButton(text='Скасувати',
                                      callback_data='cancel_create_from_vocab_name')
    # Якщо потрібно додати кнопку залишення назви
    if is_keep_old_vocab_name:
        kb.row(btn_keep_old_vocab_name)
    kb.row(btn_cancel)

    return kb.as_markup()


def get_kb_confirm_cancel(previous_stage: StopIteration) -> InlineKeyboardMarkup:
    """Повертає клавіатуру з підтвердженням або відміною скасування створення словника.
    Якщо користувач скасовує операцію, повертається до попереднього етапу, з якого був викликаний хендлер.
    При підтвердженні користувач переходить до етапу бази словників.
    """
    kb = InlineKeyboardBuilder()

    btn_agree = InlineKeyboardButton(text='✅ Так',
                                     callback_data=PaginationCallback(name='vocab_base',
                                                                      page=1,
                                                                      limit=VOCAB_PAGINATION_LIMIT).pack())
    btn_cancel = InlineKeyboardButton(text='❌ Ні',
                                      callback_data=f'back_to_{previous_stage}')

    kb.row(btn_agree,
           btn_cancel,
           width=1)
    return kb.as_markup()


def get_kb_create_vocab_note() -> InlineKeyboardMarkup:
    """Повертає клавіатуру з кнопкою скасування процесу створення словника, кнопкою зміни назви словника
    та пропуску додавання примітки.
    """
    kb = InlineKeyboardBuilder()
    btn_skip_creation_note = InlineKeyboardButton(text='Пропустити',
                                                  callback_data='skip_creation_note')
    btn_change_vocab_name = InlineKeyboardButton(text='Змінити назву словника',
                                                  callback_data='change_vocab_name')
    btn_cancel = InlineKeyboardButton(text='Скасувати',
                                      callback_data='cancel_create_from_vocab_note')

    kb.row(btn_skip_creation_note,
           btn_change_vocab_name,
           btn_cancel,
           width=1)

    return kb.as_markup()


def get_kb_create_wordpairs() -> InlineKeyboardMarkup:
    """Повертає клавіатуру з кнопкою скасування процесу створення словника,
    кнопкою збереження готового словника у БД та перевіркою поточного статусу.
    """
    kb = InlineKeyboardBuilder()
    btn_back_to_vocab_name = InlineKeyboardButton(text='Зберегти',
                                                  callback_data='back_to_vocab_name')
    btn_status = InlineKeyboardButton(text='Статус',
                                      callback_data='create_wordpairs_status')
    btn_cancel_add = InlineKeyboardButton(text='Скасувати',
                                          callback_data='cancel_create_from_wordpairs')

    kb.row(btn_back_to_vocab_name,
           btn_status,
           btn_cancel_add,
           width=1)

    return kb.as_markup()
