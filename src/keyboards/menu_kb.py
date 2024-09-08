from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton


def get_inline_kb_menu() -> InlineKeyboardMarkup:
    """Повертає клавіатуру з кнопками головного меню"""
    inline_builder = InlineKeyboardBuilder()

    btn_vocab_trainer = InlineKeyboardButton(text='📚 Словниковий тренажер',
                                             callback_data='vocab_trainer')
    btn_vocab_base = InlineKeyboardButton(text='📊 База словників',
                                          callback_data='vocab_base')
    btn_help = InlineKeyboardButton(text='⁉️ Справка',
                                    callback_data='help')

    inline_builder.row(btn_vocab_trainer,
                       btn_vocab_base,
                       btn_help,
                       width=1)

    return inline_builder.as_markup()
