from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from sqlalchemy.orm.query import Query

from db.database import Session
from db.models import User, Vocabulary
from src.keyboards.vocab_base_kb import get_inline_kb_user_vocabs
from tools.read_data import app_data

router = Router()


@router.callback_query(F.data == 'vocab_base')
async def process_btn_vocab_base(callback: CallbackQuery) -> None:
    """Відстежує натискання на кнопку бази словників.
    Відправляє користувачу список його словників.
    """
    with Session as db:
        # Отримання усіх словників, фільтруючи їх по user_id користувача
        user_vocabs: Query[Vocabulary] = db.query(Vocabulary).filter(User.id == Vocabulary.user_id)

        # Флаг, чи порожня база словників користувача
        is_vocab_base_empty: bool = len(user_vocabs.all()) == 0

        kb: InlineKeyboardMarkup = get_inline_kb_user_vocabs(user_vocabs=user_vocabs,
                                                             is_with_add_btn=is_vocab_base_empty)
        db.commit()

    # Якщо база словників порожня
    if is_vocab_base_empty:
        msg_vocab_base: str = app_data['handlers']['vocab_base']['vocab_base_is_empty']
    else:
        msg_vocab_base: str = app_data['handlers']['vocab_base']['msg_select_vocab']

    await callback.message.edit_text(text=msg_vocab_base,
                                     reply_markup=kb)


"""
@router.callback_query(F.data == 'dict_add')
async def process_btn_dict_add(callback: CallbackQuery):

    text_dict_add = 'Введите название нового словаря'
    await callback.message.edit_text(text=text_dict_add)


# Обработчик нажатия кнопок
@router.callback_query()
async def process_callback(callback: CallbackQuery):
    if callback.data.startswith('call_dict_'):
        # Получаем номер словаря из callback_data
        dict_id = int(callback.data.split('_')[1])
        with Session as db:
            all_user_dicts = db.query(
                Dictionary).filter(User.id == Dictionary.user_id)
            # dictionary_name = db.query(Dictionary).filter(
            #     Dictionary.id == dictionary_id)
            db.commit()

    inline_keyboard = get_inline_kb_dict()
    await callback.message.edit_text(
        text=all_user_dicts[dict_id],
        reply_markup=inline_keyboard)
"""
