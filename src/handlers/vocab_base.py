from typing import Any

import sqlalchemy
from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from sqlalchemy import Column
from sqlalchemy.orm.query import Query

from db.crud import get_user_vocab_by_user_id, get_user_vocab_by_vocab_id
from db.database import Session
from db.models import Translation, User, Vocabulary, Word, WordPair, WordPairTranslation, WordPairWord
from src.keyboards.vocab_base_kb import get_inline_kb_vocab_buttons
from src.keyboards.vocab_trainer_kb import get_inline_kb_all_training
from text_data import MSG_ENTER_VOCAB, MSG_ERROR_VOCAB_BASE_EMPTY, MSG_ENTER_VOCAB_FOR_TRAINING
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State


router = Router(name='vocab_base')


@router.callback_query(F.data == 'vocab_base')
async def process_vocab(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "База словників".
    Відправляє користувачу словники у вигляді кнопок.
    """
    user_id: int = callback.from_user.id

    with Session() as db:
        user_vocabs: User | None = get_user_vocab_by_user_id(db, user_id, is_all=True)  # Словники користувача
        is_vocab_base_empty: bool = get_user_vocab_by_user_id(db, user_id) is None

        if is_vocab_base_empty:
            msg_finally: str = MSG_ERROR_VOCAB_BASE_EMPTY
        else:
            msg_finally: str = MSG_ENTER_VOCAB

    # Клавіатура для відображення словників
    kb: InlineKeyboardMarkup = get_inline_kb_vocab_buttons(user_vocabs)

    current_state = 'VocabBaseState'  # Стан FSM
    await state.update_data(current_state=current_state)  # Збереження поточного стану FSM

    await callback.message.edit_text(text=msg_finally, reply_markup=kb)


@router.callback_query(F.data.startswith('select_vocab_'))
async def process_vocab_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Обробляє вибір словника"""
    vocab_id = int(callback.data.split('select_vocab_')[1])

    with Session() as db:
        user_vocab: Query[Vocabulary] = get_user_vocab_by_vocab_id(db, vocab_id)
        vocab_name = user_vocab.name

    if not user_vocab:
        await callback.message.answer('Словник не знайдено.')
        return

    data_fsm: dict = await state.get_data()  # Дані з FSM

    current_state: Any | None = data_fsm.get('current_state')  # Поточний стан FSM

    # Якщо був викликаний список словників з розділу бази словників
    if current_state == 'VocabBaseState':
        msg_finally: str = f'Ви обрали словник: {vocab_name}\nОберіть тип тренування'
        kb: InlineKeyboardMarkup = get_inline_kb_all_training()

    # Якщо був викликаний список словників з розділу тренування
    elif current_state == 'VocabTrainState':
        msg_finally: str = f'Ви обрали словник: {vocab_name}\nОберіть тип тренування'
        kb: InlineKeyboardMarkup = get_inline_kb_all_training()

    await callback.message.edit_text(text=msg_finally, reply_markup=kb)
    # ID обраного словника у FSM стані
    await state.update_data(vocab_id=vocab_id)
