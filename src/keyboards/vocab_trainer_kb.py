from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_inline_kb_all_training() -> InlineKeyboardMarkup:
    """Клавіатура з списком словникових тренувань"""
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


def get_inline_kb_process_training() -> InlineKeyboardMarkup:
    """Клавіатура з списком словникових тренувань"""
    inline_builder = InlineKeyboardBuilder()

    btn_cancel = InlineKeyboardButton(text='Скасувати',
                                      callback_data='cancel_training')

    inline_builder.row(btn_cancel)

    return inline_builder.as_markup()


def get_kb_confirm_cancel(previous_stage: StopIteration) -> InlineKeyboardMarkup:
    """Повертає клавіатуру з підтвердженням або відміною скасування тренування"""
    kb = InlineKeyboardBuilder()

    btn_agree = InlineKeyboardButton(text='✅ Так',
                                     callback_data='vocab_trainer')
    btn_cancel = InlineKeyboardButton(text='❌ Ні',
                                      callback_data=f'back_to_{previous_stage}')

    kb.row(btn_agree,
           btn_cancel,
           width=1)
    return kb.as_markup()
