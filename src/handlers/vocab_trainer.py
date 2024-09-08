from aiogram import Router, F, types

from src.keyboards.vocab_base_kb import get_inline_kb_user_vocabs
from src.keyboards.vocab_trainer_kb import get_inline_kb_all_training

from db.models import User, Vocabulary, WordPair
from db.database import Session

router = Router()


@router.callback_query(F.data == 'vocab_trainer')
async def process_btn_vocab_trainer(callback: types.CallbackQuery):
    """Відловлює натискання на кнопку тренування словникових пар.
    Відправляє клавіатуру із словниками користувача.
    """
    with Session as db:
        # Отримання всіх словників, фільтруючи по user_id користувача
        user_vocabs = db.query(Vocabulary).filter(User.id == Vocabulary.user_id)

        # Прапорець, чи порожня база словників користувача
        is_vocab_base_empty = len(user_vocabs.all()) == 0

        kb = get_inline_kb_user_vocabs(user_vocabs, is_with_add_btn=False)
        db.commit()

    if is_vocab_base_empty:
        msg_vocab_trainer = '\n'.join(['База словників порожня!',
                                      'Щоб почати тренування, потрібно додати словник у вкладці "База словників".'])
    else:
        msg_vocab_trainer = 'Оберіть словник для тренування'

    await callback.message.edit_text(text=msg_vocab_trainer, reply_markup=kb)


@router.callback_query(F.data.split('_')[0] == 'vocab_id')
async def process_btn_vocab_press(callback: types.CallbackQuery):
    """Відловлює натискання на кнопку словника.
    Відправляє клавіатуру із типами тренування
    """
    vocab_id = int(callback.data.split('_')[1])  # ID обраного словника

    with Session as db:
        # Отримання назви обраного словника із БД, виходячи з його ID
        vocab_name = (db.query(Vocabulary.dictionary_name).filter(Vocabulary.id == vocab_id))[0][0]
        msg_training_type = f'<b>{vocab_name}</b>\nОберіть тип тренування'

        # Отримання всіх словникових пар обраного словника із БД
        vocab_wordpairs = db.query(WordPair).filter(
            WordPair.vocab_id == vocab_id)

        for i in vocab_wordpairs:
            print(i.word_1, end=' & ')
            print(i.word_2)

        kb = get_inline_kb_all_training()
        db.commit()

    await callback.message.edit_text(text=msg_training_type,
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
