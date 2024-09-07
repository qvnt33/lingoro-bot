from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from sqlalchemy.orm.query import Query

from db.database import Session
from db.models import Dictionary, User

from src.keyboards.dict_base_kb import get_inline_kb_dict

router = Router()


@router.callback_query(F.data == 'dict_base')
async def process_btn_dict_base(callback: CallbackQuery) -> None:
    """Відстежує натискання на кнопку "База словників".
    Відправляє користувачу список його словників.
    """
    with Session as db:
        # Отримує всі словники, фільтруючи їх по user_id користувача
        user_dicts: Query[Dictionary] = db.query(Dictionary).filter(User.id == Dictionary.user_id)

        # Отримує прапорець, чи порожня база словників користувача
        is_dict_base_empty: bool = len(user_dicts.all()) == 0

        kb: InlineKeyboardMarkup = get_inline_kb_dict(user_dicts=user_dicts,
                                                      is_with_add_btn=is_dict_base_empty)

        db.commit()

    if is_dict_base_empty:
        msg_dict_base = ('Ваша база словників порожня!\n'
                         'Для додавання словника, натисніть на кнопку "Додати словник"')
    else:
        msg_dict_base = 'Оберіть словник для його редагування та перегляду вмісту.'(
            "Выберите словарь для его редактирования и просмотра содержимого."
        )

    await callback.message.edit_text(text=msg_dict_base, reply_markup=kb)


"""
@router.callback_query(F.data == 'dict_add')
async def process_btn_dict_add(callback: CallbackQuery):
    """ """
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
