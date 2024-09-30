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
from tools.escape_markdown import escape_markdown
router = Router(name='create_vocab')


@router.callback_query(F.data == 'create_vocab')
async def process_create_vocab(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Додати новий словник".
    Виконується процес створення словника.
    """
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
    vocab_name: str = message.text  # Назва словника, створення користувачем

    with Session() as db:
        # Валідатор для перевірки коректності назви
        validator = VocabNameValidator(
            name=vocab_name,
            min_length=MIN_LENGTH_VOCAB_NAME,
            max_length=MAX_LENGTH_VOCAB_NAME,
            db=db)

    # Якщо назва коректна
    if validator.is_valid(user_id=user_id):
        msg_vocab_name: str = f'*Назва словника:* {escape_markdown(vocab_name)}\n\nВведіть *примітку* до словника.\nЯкщо примітка до словника не потрібна - натисніть на кнопку "Пропустити".'
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_note()  # Клавіатура для створення примітки

        await state.update_data(vocab_name=vocab_name)  # Збереження назви в кеш FSM
        await state.set_state(VocabCreation.waiting_for_vocab_note)  # Переведення FSM у стан очікування примітки
    else:
        # Якщо назва некоректна
        formatted_errors: str = validator.format_errors()  # Відформатований список помилок
        msg_vocab_name: str = f'❌ *Є помилки у назві словника "{escape_markdown(vocab_name)}"*\n{formatted_errors}\n\nБудь ласка, введіть іншу *назву*:'
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

    # Валідатор для перевірки примітки
    validator = VocabNoteValidator(note=vocab_note,
                                   min_length=MIN_LENGTH_VOCAB_NOTE,
                                   max_length=MAX_LENGTH_VOCAB_NOTE)

    # Якщо примітка коректна
    if validator.is_valid():
        msg_vocab_note: str = f'*Назва словника:* {vocab_name}\n*Примітка до словника:* {vocab_note}\n\nВідправте *словникові пари* для цього словника у форматі:\n_word1, word2 : translation1, translation2 : annotation_\n- *word2*, *translation2* та *annotation* — необов\'язкові поля.'
        kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs()  # Клавіатура для введення назви

        await state.update_data(vocab_note=vocab_note)  # Збереження примітки в кеш FSM
        await state.set_state(VocabCreation.waiting_for_wordpairs)  # Переведення FSM у стан очікування словникових пар
    else:
        # Якщо примітка некоректна
        formatted_errors: str = validator.format_errors()  # Відформатований список помилок
        msg_vocab_note: str = f'❌ *Є помилки у примітці до словника:*\n{formatted_errors}\n\nБудь ласка, введіть іншу *примітку*.\nЯкщо примітка до словника не потрібна - натисніть на кнопку "*Пропустити*".'

    await message.answer(text=msg_vocab_note, reply_markup=kb)


@router.message(VocabCreation.waiting_for_wordpairs)
async def process_creating_wordpairs(message: Message, state: FSMContext) -> None:
    """Обробляє словникові пари до словника, які ввів користувач"""
    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()  # Клавіатура для створення примітки

    await state.update_data(vocab_note=None)  # Збереження примітка в кеш FSM (якщо натисне кнопку пропуску)

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM

    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника
    vocab_note: str = message.text  # Примітка, введена користувачем

    # Валідатор для перевірки примітки
    validator = VocabNoteValidator(note=vocab_note,
                                   min_length=MIN_LENGTH_VOCAB_NOTE,
                                   max_length=MAX_LENGTH_VOCAB_NOTE)

    # Якщо примітка коректна
    if validator.is_valid():
        msg_vocab_note: str = f'*Назва словника:* {vocab_name}\n*Примітка до словника:* {vocab_note}\n\nВідправте *словникові пари* для словника:'
        kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs()  # Клавіатура для введення назви

        await state.update_data(vocab_note=vocab_note)  # Збереження примітки в кеш FSM
        await state.set_state(VocabCreation.waiting_for_wordpairs)  # Переведення FSM у стан очікування словникових пар
    else:
        # Якщо примітка некоректна
        formatted_errors: str = validator.format_errors()  # Відформатований список помилок
        msg_vocab_note: str = f'❌ *Є помилки у примітці до словника:*\n{formatted_errors}\n\nБудь ласка, введіть іншу *примітку*.\nЯкщо примітка до словника не потрібна - натисніть на кнопку "*Пропустити*".'

    await message.answer(text=msg_vocab_note, reply_markup=kb)


# Хендлер для повернення до введення назви словника
@router.callback_query(F.data == 'change_vocab_name')
async def process_change_vocab_name(callback: CallbackQuery, state: FSMContext) -> None:
    """Змінює назву словника при створенні словника"""
    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника

    # Клавіатура для створення назви з кнопкою "Залишити поточну назву"
    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name(keep_old_vocab_name=True)

    await callback.message.edit_text(text=f'*Поточна назва:* {vocab_name}\n\nВведіть іншу *назву* словника:', reply_markup=kb)
    await state.set_state(VocabCreation.waiting_for_vocab_name)


@router.callback_query(F.data == 'keep_old_vocab_name')
async def process_keep_old_vocab_name(callback: CallbackQuery, state: FSMContext) -> None:
    """Після натискання на кнопку "Залишити поточну назву", залишає поточну назву та переходить до створення примітки"""
    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_note()  # Клавіатура для примітки
    # Отримуємо дані з FSM
    data_fsm: Dict[str, Any] = await state.get_data()
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника

    msg_vocab_name: str = f'*Назва словника:* {vocab_name}\n\nВведіть *примітку* до словника\nЯкщо примітка до словника не потрібна - натисніть на кнопку "*Пропустити*".'
    await callback.message.edit_text(text=msg_vocab_name, reply_markup=kb)
    await state.set_state(VocabCreation.waiting_for_vocab_note)





# Хендлер для повернення до введення примітки



# Хендлер для підтвердження скасування
@router.callback_query(F.data.startswith('cancel_from_'))
async def process_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    """Обробляє натискання на кнопки скасування на різних етапах."""
    stage = callback.data[len('cancel_from_'):]  # Витягуємо стан після 'cancel_'

    cancel_text = 'Ви дійсно хочете *скасувати* створення словника?'
    await state.clear()
    kb: InlineKeyboardMarkup = get_inline_kb_confirm_cancel(callback_data_to_back=stage, state=state)

    await callback.message.edit_text(text=cancel_text, reply_markup=kb)


def get_inline_kb_confirm_cancel(callback_data_to_back: str, state: FSMContext) -> InlineKeyboardMarkup:
    """Генерує клавіатуру з підтвердженням або відміною для будь-якого етапу."""
    kb = InlineKeyboardBuilder()

    btn_agree = InlineKeyboardButton(text='✅ Так',
                                     callback_data=PaginationCallback(name='vocab_base',
                                                                      page=1,
                                                                      limit=VOCAB_PAGINATION_LIMIT).pack())

    btn_cancel = InlineKeyboardButton(text='❌ Ні', callback_data=f'back_to_{callback_data_to_back}')

    kb.row(btn_agree, btn_cancel, width=1)
    return kb.as_markup()


# Хендлер для натискання "Ні" при скасуванні
@router.callback_query(F.data.startswith('back_to_'))
async def process_back_to(callback: CallbackQuery, state: FSMContext) -> None:
    """Обробляє натискання на кнопку 'Ні' та повертає користувача до правильного етапу."""
    stage = callback.data[len('back_to_'):]  # Все, що йде після 'back_to_'

    if stage == 'vocab_name':
        # Повертаємо користувача до введення назви
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()
        await callback.message.edit_text(text='Введіть *назву* словника:', reply_markup=kb)
        await state.set_state(VocabCreation.waiting_for_vocab_name)
    elif stage == 'vocab_note':
        # Повертаємо користувача до введення примітки
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_note()
        await callback.message.edit_text(text='Введіть *примітку* до словника:', reply_markup=kb)
        await state.set_state(VocabCreation.waiting_for_vocab_note)
