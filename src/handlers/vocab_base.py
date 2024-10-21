from typing import Any, Dict

import sqlalchemy
from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from sqlalchemy import Column
from sqlalchemy.orm.query import Query

from db.crud import get_user_vocab_by_user_id, get_user_vocab_by_vocab_id, get_vocab_details_by_vocab_id, get_wordpairs_by_vocab_id
from db.database import Session
from db.models import Translation, User, Vocabulary, Word, WordPair, WordPairTranslation, WordPairWord
from src.keyboards.vocab_base_kb import get_inline_kb_vocab_buttons, get_inline_kb_vocab_options
from src.keyboards.vocab_trainer_kb import get_inline_kb_all_training
from text_data import MSG_ENTER_VOCAB, MSG_ERROR_VOCAB_BASE_EMPTY
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from typing import List, Tuple


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
    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM

    vocab_id = int(callback.data.split('select_vocab_')[1])

    with Session() as db:
        all_wordpairs_data: List[Dict] = get_wordpairs_by_vocab_id(db, vocab_id)
        vocab_details: dict = get_vocab_details_by_vocab_id(db, vocab_id)

    vocab_name: str = vocab_details['name']
    vocab_note: str = vocab_details['note']

    current_state: Any | None = data_fsm.get('current_state')  # Поточний стан FSM

    # Якщо був викликаний список словників з розділу бази словників
    if current_state == 'VocabBaseState':
        kb: InlineKeyboardMarkup = get_inline_kb_vocab_options()
        msg_finally: str = (
        f'Назва словника: {vocab_name}\n'
        f'Примітка: {vocab_note or 'Відсутня'}\n'
        f'Кількість словникових пар: {len(all_wordpairs_data)}\n\n'
        f'Словникові пари:\n')

        for idx, wordpairs_data in enumerate(all_wordpairs_data, start=1):
            words_lst: List[Tuple[str, str]] = wordpairs_data['words']
            translations_lst: List[Tuple[str, str]] = wordpairs_data['translations']
            annotation: str = wordpairs_data['annotation'] or 'Немає анотації'

            words_part: str = ', '.join([f'{word} [{transcription}]'
                                    if transcription else word
                                    for word, transcription in words_lst])
            translations_part: str = ', '.join([f'{translation} [{transcription}]'
                                        if transcription else translation
                                        for translation, transcription in translations_lst])

            msg_finally += f'{idx}. {words_part} : {translations_part} : {annotation}\n'
    # Якщо був викликаний список словників з розділу тренування
    elif current_state == 'VocabTrainState':
        msg_finally: str = f'Ви обрали словник: {vocab_name}\nОберіть тип, будь-ласка, тип тренування.'
        kb: InlineKeyboardMarkup = get_inline_kb_all_training()

    # ID обраного словника у FSM стані
    await state.update_data(vocab_id=vocab_id)

    await callback.message.edit_text(text=msg_finally, reply_markup=kb)
