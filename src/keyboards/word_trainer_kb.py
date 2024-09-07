from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton


def get_inline_kb_all_training() -> InlineKeyboardMarkup:
    """Повертає клавіатуру зі списком тренувань у вигляді кнопок"""
    inline_builder = InlineKeyboardBuilder()

    btn_train_direct = InlineKeyboardButton(text='Прямий переклад (Word1 → Word2)',
                                            callback_data='direct_translation')
    btn_train_revers = InlineKeyboardButton(text='Зворотній переклад (Word2 → Word1)',
                                            callback_data='revers_translation')
    btn_train_change_dict = InlineKeyboardButton(text='Змінити словник',
                                                 callback_data='word_trainer')
    btn_menu = InlineKeyboardButton(text='Головне меню',
                                    callback_data='menu')

    inline_builder.row(btn_train_direct,
                       btn_train_revers,
                       btn_train_change_dict,
                       btn_menu,
                       width=1)

    return inline_builder.as_markup()
