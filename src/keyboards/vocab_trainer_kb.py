from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_inline_kb_all_training() -> InlineKeyboardMarkup:
    """Повертає клавіатуру з списком словникових тренувань"""
    inline_builder = InlineKeyboardBuilder()

    btn_direct_translation = InlineKeyboardButton(text='Прямий переклад (Word A → Word B)',
                                                  callback_data='direct_translation')
    btn_reverse_translation = InlineKeyboardButton(text='Зворотній переклад (Word B → Word A)',
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
