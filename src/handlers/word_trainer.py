from aiogram import Router, F, types

from src.keyboards.dict_base_kb import get_inline_kb_dict
from src.keyboards.word_trainer_kb import get_inline_kb_all_training

from db.models import Dictionary, User, WordPair
from db.database import Session

router = Router()


@router.callback_query(F.data == 'word_trainer')
async def process_btn_word_trainer(callback: types.CallbackQuery):
    """Отлавливаем нажатие на кнопку тренировки.
    Отправляем клавиатуру с словарями пользователя"""
    with Session as db:
        # Получаем все словари, фильтруя по user_id пользователя
        user_dicts = db.query(Dictionary).filter(User.id == Dictionary.user_id)

        # База словарей пользователя пустая
        dict_base_is_empty = len(user_dicts.all()) == 0

        kb = get_inline_kb_dict(user_dicts, is_with_add_btn=False)
        db.commit()

    if dict_base_is_empty:
        msg_word_trainer = '\n'.join(['База словарей пуста!',
                                      'Чтобы начать тренировку, нужно добавить словарь во вкладке "База словарей".'])
    else:
        msg_word_trainer = 'Выберите словарь для тренировки'

    await callback.message.edit_text(text=msg_word_trainer, reply_markup=kb)


@router.callback_query(F.data.split('_')[0] == 'calldict')
async def process_btn_dict(callback: types.CallbackQuery):
    """Отлавливаем нажатие на кнопку словаря.
    Отправляем клавиатуру с тренировками"""
    dict_id = int(callback.data.split('_')[1])  # id выбранного словаря

    with Session as db:
        # Получаем имя выбранного словаря из БД, исходя из его id
        dict_name = (db.query(Dictionary.dictionary_name).filter(Dictionary.id == dict_id))[0][0]
        msg_dict = f'<b>{dict_name}</b>\nВыберите тип тренировки'
        # Все словарные пары выбранного словаря
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
    """Отлавливаем нажатие на кнопку тренировки 'Прямой перевод'"""

    msg_train_direct = 'Вы выбрали тренировку "Прямой перевод"'
    # kb = get_inline_kb_dict()

    # await callback.message.edit_text(text=msg_train_direct, reply_markup=kb)


@router.callback_query(F.data == 'revers_translation')
async def process_btn_revers_translation(callback: types.CallbackQuery):
    """Отлавливаем нажатие на кнопку тренировки 'Обратный перевод'"""
    msg_train_direct = 'Вы выбрали тренировку "Обратный перевод"'
    # kb = get_inline_kb_dict()

    # await callback.message.edit_text(text=msg_train_direct, reply_markup=kb)
