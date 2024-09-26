
from typing import Any, Dict
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from config import MIN_LENGTH_VOCAB_NAME, MAX_LENGTH_VOCAB_NAME, MIN_LENGTH_VOCAB_NOTE, MAX_LENGTH_VOCAB_NOTE
from db.database import Session
from src.keyboards.create_vocab_kb import get_inline_kb_confirm_cancel, get_inline_kb_create_vocab
from src.validators.vocab_name_validator import VocabNameValidator
from src.validators.vocab_note_validator import VocabNoteValidator
from tools.read_data import app_data

router = Router(name='create_vocab')


class VocabCreation(StatesGroup):
    waiting_for_vocab_name = State()  # Стан очікування назви словника
    waiting_for_vocab_note = State()  # Стан очікування примітки до словника


@router.callback_query(F.data == 'create_vocab')
async def process_create_vocab(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Додати новий словник".
    Виконується процес створення словника.
    """
    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab()
    await callback.message.edit_text(text='Введіть назву словника:', reply_markup=kb)

    # Перевод FSM у стан очікування назви
    await state.set_state(VocabCreation.waiting_for_vocab_name)


@router.message(VocabCreation.waiting_for_vocab_name)
async def process_vocab_name(message: Message, state: FSMContext) -> None:
    """Обробляє назву словника, яку ввів користувач"""
    user_id: int = message.from_user.id

    vocab_name: str | None = message.text  # Назва словника, введена користувачем

    with Session() as db:
        # Валідатор для перевірки назви словника
        validator = VocabNameValidator(
            name=vocab_name,
            min_length_vocab_name=MIN_LENGTH_VOCAB_NAME,
            max_length_vocab_name=MAX_LENGTH_VOCAB_NAME,
            db=db)

    if validator.is_valid(user_id=user_id):
        # Повідомлення, що назва валідна
        msg_vocab_name: str = app_data['create_vocab']['name']['correct'].format(vocab_name)

        # Клавіатура з кнопкою скасування та пропуску додавання нотатки
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab(is_with_skip_note=True)

        # Збереження назви в кеш FSM
        await state.update_data(vocab_name=vocab_name)
        # Перевод FSM у стан очікування примітки до словника
        await state.set_state(VocabCreation.waiting_for_vocab_note)
    else:
        # Форматування помилок
        formatted_errors: str = '\n'.join([f'{num}. {error}' for num, error in enumerate(iterable=validator.errors,
                                                                                         start=1)])
        # Повідомлення про не валідну назву та відправлення помилок
        msg_vocab_name: str = app_data['create_vocab']['name']['incorrect'].format(formatted_errors)

        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab()

        # Перевод FSM у стан очікування назви
        await state.set_state(VocabCreation.waiting_for_vocab_name)

    # Надсилаємо повідомлення користувачу
    await message.answer(text=msg_vocab_name, reply_markup=kb)


@router.message(VocabCreation.waiting_for_vocab_note)
async def process_vocab_note(message: Message, state: FSMContext) -> None:
    """Обробляє примітку до словника, яку ввів користувач"""
    user_id: int = message.from_user.id

    vocab_note: str | None = message.text  # Назва словника, введена користувачем

    # Клавіатура з кнопкою скасування та пропуску додавання нотатки
    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab(is_with_skip_note=True)

    # Валідатор для перевірки примітки до словника
    validator = VocabNoteValidator(note=vocab_note,
                                   min_length_vocab_note=MIN_LENGTH_VOCAB_NOTE,
                                   max_length_vocab_note=MAX_LENGTH_VOCAB_NOTE)

    if validator.is_valid():
        msg_vocab_note: str = app_data['create_vocab']['note']['correct']
        await state.update_data(vocab_name=msg_vocab_note)  # Збереження назви в кеш FSM

    else:
        # Якщо є помилки, форматуємо їх і просимо ввести іншу назву
        formatted_errors: str = '\n'.join([f'{num}. {error}' for num, error in enumerate(validator.errors, start=1)])
        msg_vocab_note: str = app_data['create_vocab']['note']['incorrect'].format(formatted_errors)

        # Перевод FSM у стан очікування примітки до словника
        await state.set_state(VocabCreation.waiting_for_vocab_note)

    # Надсилаємо повідомлення користувачу
    await message.answer(text=msg_vocab_note, reply_markup=kb)


@router.callback_query(F.data == 'cancel_create_vocab')
async def process_confirm_cancel(callback: CallbackQuery) -> None:
    """Відстежує натискання на кнопку "Скасувати".
    Відправляється кнопки з підтвердженням скасування.
    """
    kb: InlineKeyboardMarkup = get_inline_kb_confirm_cancel()

    await callback.message.edit_text(text='Ви дійсно хочете скасувати створення словника?', reply_markup=kb)
