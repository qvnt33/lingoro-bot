import logging
from typing import Any, Dict

from .callback_data import PaginationCallback
from .vocab_base import process_vocab_base
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import (
    MAX_LENGTH_VOCAB_NAME,
    MAX_LENGTH_VOCAB_NOTE,
    MIN_LENGTH_VOCAB_NAME,
    MIN_LENGTH_VOCAB_NOTE,
    VOCAB_PAGINATION_LIMIT,
)
from db.database import Session
from src.fsm.states import VocabCreation
from src.keyboards.create_vocab_kb import get_inline_kb_create_vocab_name, get_inline_kb_create_vocab_note, get_inline_kb_create_wordpairs
from src.validators.vocab_name_validator import VocabNameValidator
from src.validators.vocab_note_validator import VocabNoteValidator
from tools.read_data import app_data

router = Router(name='create_vocab')


@router.callback_query(F.data == 'create_vocab')
async def process_create_vocab(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Додати новий словник".
    Виконується процес створення словника.
    """
    logging.info("Користувач почав процес створення нового словника")  # Логування події
    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()   # Клавіатура для створення назви
    await callback.message.edit_text(text='Введіть *назву* словника:', reply_markup=kb)

    # Переведення FSM у стан очікування назви словника
    await state.set_state(VocabCreation.waiting_for_vocab_name)


@router.message(VocabCreation.waiting_for_vocab_name)
async def process_vocab_name(message: Message, state: FSMContext) -> None:
    """Обробляє назву словника, яку ввів користувач.
    Переходить до процесу створення примітки до словника, якщо назва коректна.
    """
    user_id: int = message.from_user.id
    vocab_name: str = message.text  # Назва словника, створена користувачем

    logging.debug(f"Користувач ввів назву словника: {vocab_name}")  # Логування введеної назви

    with Session() as db:
        # Валідатор для перевірки коректності назви
        validator = VocabNameValidator(
            name=vocab_name,
            min_length=MIN_LENGTH_VOCAB_NAME,
            max_length=MAX_LENGTH_VOCAB_NAME,
            db=db)

    # Якщо назва коректна
    if validator.is_valid(user_id=user_id):
        logging.info(f"Назва словника '{vocab_name}' пройшла валідацію")  # Логування успішної валідації
        msg_vocab_name: str = f'*Назва словника:* {vocab_name}\n\nВведіть *примітку* до словника.\nЯкщо примітка до словника не потрібна - натисніть на кнопку "Пропустити".'
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_note()  # Клавіатура для створення примітки

        await state.update_data(vocab_name=vocab_name)  # Збереження назви в кеш FSM
        await state.set_state(VocabCreation.waiting_for_vocab_note)  # Переведення FSM у стан очікування примітки
    else:
        # Якщо назва некоректна
        logging.warning(f"Назва словника '{vocab_name}' не пройшла валідацію")  # Логування помилок валідації
        formatted_errors: str = validator.format_errors()  # Відформатований список помилок
        logging.warning(f"Назва словника '{vocab_name}' не пройшла валідацію. Помилки:\n{formatted_errors}")
        msg_vocab_name: str = f'❌ *Є помилки у назві словника "{vocab_name}"*\n{formatted_errors}\n\nБудь ласка, введіть іншу *назву*:'
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()  # Клавіатура для введення назви

    await message.answer(text=msg_vocab_name, reply_markup=kb)


@router.message(VocabCreation.waiting_for_vocab_note)
async def process_vocab_note(message: Message, state: FSMContext) -> None:
    """Обробляє примітку до словника, яку ввів користувач.
    Переходить до процесу додавання словникових пар, якщо примітка коректна.
    """
    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()  # Клавіатура для створення примітки

    await state.update_data(vocab_note=None)  # Збереження примітки в кеш FSM (якщо натисне кнопку пропуску)

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM

    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника
    vocab_note: str = message.text  # Примітка, введена користувачем

    logging.debug(f"Користувач ввів примітку до словника: {vocab_note}")  # Логування введеної примітки

    # Валідатор для перевірки примітки
    validator = VocabNoteValidator(note=vocab_note,
                                   min_length=MIN_LENGTH_VOCAB_NOTE,
                                   max_length=MAX_LENGTH_VOCAB_NOTE)

    # Якщо примітка коректна
    if validator.is_valid():
        logging.info(f"Примітка '{vocab_note}' пройшла валідацію")  # Логування успішної валідації
        msg_vocab_note: str = f'*Назва словника:* {vocab_name}\n*Примітка до словника:* {vocab_note}\n\nВідправте *словникові пари* для цього словника у форматі:\n_word1, word2 : translation1, translation2 : annotation_\n- *word2*, *translation2* та *annotation* — необов\'язкові поля.'
        kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs()  # Клавіатура для введення назви

        await state.update_data(vocab_note=vocab_note)  # Збереження примітки в кеш FSM
        await state.set_state(VocabCreation.waiting_for_wordpairs)  # Переведення FSM у стан очікування словникових пар
    else:
        # Якщо примітка некоректна
        logging.warning(f"Примітка '{vocab_note}' не пройшла валідацію")  # Логування помилок валідації
        formatted_errors: str = validator.format_errors()  # Відформатований список помилок
        msg_vocab_note: str = f'❌ *Є помилки у примітці до словника:*\n{formatted_errors}\n\nБудь ласка, введіть іншу *примітку*.\nЯкщо примітка до словника не потрібна - натисніть на кнопку "*Пропустити*".'

    await message.answer(text=msg_vocab_note, reply_markup=kb)

# Хендлер для повернення до введення назви словника
@router.callback_query(F.data == 'change_vocab_name')
async def process_change_vocab_name(callback: CallbackQuery, state: FSMContext) -> None:
    """Змінює назву словника при створенні словника"""
    logging.info("Користувач вирішив змінити назву словника")  # Логування дії зміни назви
    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника

    # Клавіатура для створення назви з кнопкою "Залишити поточну назву"
    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name(keep_old_vocab_name=True)

    await callback.message.edit_text(text=f'*Поточна назва:* {vocab_name}\n\nВведіть іншу *назву* словника:', reply_markup=kb)
    await state.set_state(VocabCreation.waiting_for_vocab_name)


@router.callback_query(F.data == 'keep_old_vocab_name')
async def process_keep_old_vocab_name(callback: CallbackQuery, state: FSMContext) -> None:
    """Після натискання на кнопку "Залишити поточну назву", залишає поточну назву та переходить до створення примітки"""
    logging.info("Користувач вирішив залишити поточну назву словника")  # Логування збереження старої назви
    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_note()  # Клавіатура для примітки
    # Отримуємо дані з FSM
    data_fsm: Dict[str, Any] = await state.get_data()
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника

    msg_vocab_name: str = f'*Назва словника:* {vocab_name}\n\nВведіть *примітку* до словника\nЯкщо примітка до словника не потрібна - натисніть на кнопку "*Пропустити*".'
    await callback.message.edit_text(text=msg_vocab_name, reply_markup=kb)
    await state.set_state(VocabCreation.waiting_for_vocab_note)
