from aiogram import Router, F, types

from src.keyboards.dict_base_kb import get_inline_kb_dict
from src.keyboards.word_trainer_kb import get_inline_kb_all_training

from db.models import Dictionary, User, WordPair
from db.database import Session

router = Router()


@router.callback_query(F.data == 'word_trainer')
async def process_btn_word_trainer(callback: types.CallbackQuery):
    """Відловлює натискання на кнопку 'word_trainer'.
    Відправляє клавіатуру із словниками користувача
    """
    with Session as db:
        # Отримання всіх словників, фільтруючи по user_id користувача
        user_dicts = db.query(Dictionary).filter(User.id == Dictionary.user_id)

        # Прапорець, чи порожня база словників користувача
        dict_base_is_empty = len(user_dicts.all()) == 0

        kb = get_inline_kb_dict(user_dicts, is_with_add_btn=False)
        db.commit()

    if dict_base_is_empty:
        msg_word_trainer = '\n'.join(['База словників порожня!',
                                      'Щоб почати тренування, потрібно додати словник у вкладці "База словників".'])
    else:
        msg_word_trainer = 'Оберіть словник для тренування'

    await callback.message.edit_text(text=msg_word_trainer, reply_markup=kb)


@router.callback_query(F.data.split('_')[0] == 'calldict')
async def process_btn_dict(callback: types.CallbackQuery):
    """Відловлює натискання на кнопку словника.
    Відправляє клавіатуру із типами тренування
    """
    dict_id = int(callback.data.split('_')[1])  # ID обраного словника

    with Session as db:
        # Отримання назви обраного словника із БД, виходячи з його ID
        dict_name = (db.query(Dictionary.dictionary_name).filter(Dictionary.id == dict_id))[0][0]
        msg_dict = f'<b>{dict_name}</b>\nОберіть тип тренування'

        # Отримання всіх словникових пар обраного словника із БД
        dict_wordpairs = db.query(WordPair).filter(
            WordPair.dictionary_id == dict_id)

        for i in dict_wordpairs:
            print(i.word_1, end=' & ')
            print(i.word_2)

        kb = get_inline_kb_all_training()
        db.commit()

    await callback.message.edit_text(text=msg_dict,
                                     reply_markup=kb,
                                     parse_mode='html')


@router.callback_query(F.data == 'direct_translation')
async def process_btn_direct_translation(callback: types.CallbackQuery):
    """Відловлює натискання на кнопку типу тренування 'direct_translation'"""
    msg_train_direct = 'Ви обрали тип тренування "Прямий переклад"'
    # kb = get_inline_kb_dict()

    # await callback.message.edit_text(text=msg_train_direct, reply_markup=kb)


@router.callback_query(F.data == 'revers_translation')
async def process_btn_revers_translation(callback: types.CallbackQuery):
    """Відловлює натискання на кнопку типу тренування 'revers_translation'"""
    msg_train_direct = 'Ви обрали тип тренування "Зворотній переклад"'
    # kb = get_inline_kb_dict()

    # await callback.message.edit_text(text=msg_train_direct, reply_markup=kb)
