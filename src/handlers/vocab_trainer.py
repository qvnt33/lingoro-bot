from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from sqlalchemy.orm.query import Query

from db.crud import get_user_vocab_by_user_id
from db.database import Session
from db.models import User, Vocabulary, WordPair
from src.keyboards.vocab_base_kb import get_inline_kb_vocab_buttons
from src.keyboards.vocab_trainer_kb import get_inline_kb_all_training
from text_data import MSG_ENTER_VOCAB, MSG_ERROR_VOCAB_BASE_EMPTY
from tools.read_data import app_data
from aiogram.fsm.context import FSMContext

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

router = Router('vocab_trainer')


@router.callback_query(F.data == 'vocab_trainer')
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
    kb: InlineKeyboardMarkup = get_inline_kb_vocab_buttons(user_vocabs, is_with_create_vocab=False)

    current_state = 'VocabTrainState'  # Стан FSM
    await state.update_data(current_state=current_state)  # Збереження поточного стану FSM

    await callback.message.edit_text(text=msg_finally, reply_markup=kb)



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
