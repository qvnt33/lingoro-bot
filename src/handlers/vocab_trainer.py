from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from sqlalchemy.orm.query import Query

from db.database import Session
from db.models import User, Vocabulary, WordPair
from src.keyboards.vocab_base_kb import get_inline_kb_user_vocabs
from src.keyboards.vocab_trainer_kb import get_inline_kb_all_training
from tools.read_data import app_data

router = Router()


@router.callback_query(F.data == 'vocab_trainer')
async def process_btn_vocab_trainer(callback: CallbackQuery) -> None:
    """Відстежує натискання на кнопку словникових тренувань.
    Відправляє користувачу список його словників.
    """
    with Session as db:
        # Отримання всіх словників, фільтруючи по user_id користувача
        user_vocabs: Query[Vocabulary] = db.query(Vocabulary).filter(User.id == Vocabulary.user_id)

        # Флаг, чи порожня база словників користувача
        is_vocab_base_empty: bool = len(user_vocabs.all()) == 0

        kb: InlineKeyboardMarkup = get_inline_kb_user_vocabs(user_vocabs,
                                                             is_with_add_btn=False)
        db.commit()

    # Якщо база словників порожня
    if is_vocab_base_empty:
        msg_vocab_trainer: str = app_data['handlers']['vocab_trainer']['vocab_base_is_empty']
    else:
        msg_vocab_trainer: str = app_data['handlers']['vocab_trainer']['msg_select_vocab']

    await callback.message.edit_text(text=msg_vocab_trainer,
                                     reply_markup=kb)


@router.callback_query(F.data.split('_')[0] == 'vocab_id')
async def process_btn_user_vocab(callback: CallbackQuery) -> None:
    """Відстежує натискання на кнопку конкретного словника.
    Відправляє користувачу список типів тренування.
    """
    vocab_id = int(callback.data.split('_')[1])  # ID обраного словника

    with Session as db:
        # Отримання назви обраного словника із БД, виходячи з його ID
        vocab_name: str = (db.query(Vocabulary.dictionary_name).filter(Vocabulary.id == vocab_id))[0][0]
        msg_training_type: str = app_data['handlers']['vocab_trainer']['msg_select_training_type'].format(
            vocab_name=vocab_name)

        # Отримання всіх словникових пар обраного словника із БД
        vocab_wordpairs: Query[WordPair] = db.query(WordPair).filter(
            WordPair.vocab_id == vocab_id)

        kb: InlineKeyboardMarkup = get_inline_kb_all_training()
        db.commit()

    await callback.message.edit_text(text=msg_training_type,
                                     reply_markup=kb)


"""
@router.callback_query(F.data == 'direct_translation')
async def process_btn_direct_translation(callback: CallbackQuery) -> None:
    msg_train_direct = app_data['handlers']['vocab_trainer']['msg_selected_direct_translation']
    # kb = get_inline_kb_dict()

    # await callback.message.edit_text(text=msg_train_direct, reply_markup=kb)


@router.callback_query(F.data == 'reverse_translation')
async def process_btn_reverse_translation(callback: CallbackQuery):
    msg_train_direct = app_data['handlers']['vocab_trainer']['msg_selected_reverse_translation']
    # kb = get_inline_kb_dict()

    # await callback.message.edit_text(text=msg_train_direct, reply_markup=kb)
"""
