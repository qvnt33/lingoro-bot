from typing import Any, Dict

from .vocab_base import process_vocab_base
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
from db.database import Session
from src.fsm.states import VocabCreation
from src.keyboards.create_vocab_kb import (
    get_kb_confirm_cancel,
    get_kb_create_vocab_name,
    get_kb_create_vocab_note,
    get_kb_create_wordpairs,
)
from src.validators.vocab_name_validator import VocabNameValidator
from src.validators.vocab_note_validator import VocabNoteValidator
from src.validators.wordpair.wordpair_validator import WordPairValidator

# from tools.escape_markdown import escape_markdown
from tools.read_data import app_data
from tools.message_formatter import create_vocab_message
from config import DEFAULT_VOCAB_NOTE
from messages import MSG_ENTER_NEW_VOCAB_NAME, MSG_ENTER_VOCAB_NAME,MSG_ERROR_VOCAB_SAME_NAME,MSG_SUCCESS_VOCAB_NAME_CREATED,MSG_VOCAB_NAME_ERRORS, MSG_VOCAB_NOTE_ERRORS, MSG_VOCAB_WORDPAIRS_SAVED_INSTRUCTIONS

router = Router(name='create_vocab')


@router.callback_query(F.data == 'create_vocab')
async def process_create_vocab(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Додати новий словник".
    Виконується процес створення словника.
    """
    logging.info(f'ПОЧАТОК: СТВОРЕННЯ СЛОВНИКА. USER_ID: {callback.from_user.id}')

    await state.clear()  # Очищення FSM-кеш

    kb: InlineKeyboardMarkup = get_kb_create_vocab_name()  # Клавіатура для створення назви словника

    msg_enter_name: str = MSG_ENTER_VOCAB_NAME
    msg_finally: str = create_vocab_message(content=msg_enter_name)

    await callback.message.edit_text(text=msg_finally, reply_markup=kb)

    fsm_state: State = VocabCreation.waiting_for_vocab_name  # FSM стан очікування назви
    await state.set_state(fsm_state)  # Переведення у новий FSM стан
    logging.info(f'FSM стан змінено на "{fsm_state}"')


@router.message(VocabCreation.waiting_for_vocab_name)
async def process_vocab_name(message: Message, state: FSMContext) -> None:
    """Обробляє назву словника, яку ввів користувач"""
    data_fsm: dict = await state.get_data()  # Дані з FSM

    user_id: int = message.from_user.id

    vocab_name: str = message.text.strip()  # Введена назва словника (без зайвих пробілів)
    vocab_name_old: Any | None = data_fsm.get('vocab_name')  # Стара назва словника

    logging.info(f'Користувач ввів назву до словника: "{vocab_name}"')

    kb: InlineKeyboardMarkup = get_kb_create_vocab_name()  # Клавіатура для створення назви словника

    # Якщо введена назва словника збігається з поточною
    if vocab_name_old is not None and vocab_name.lower() == vocab_name_old.lower():
        logging.warning(f'Назва до словника "{vocab_name}" вже знаходиться у базі користувача')

        # Клавіатура для створення назви словника з кнопкою зберігання назви
        kb: InlineKeyboardMarkup = get_kb_create_vocab_name(is_keep_old_vocab_name=True)
        msg_finally: str = create_vocab_message(vocab_name=vocab_name_old, content=MSG_ERROR_VOCAB_SAME_NAME)

        await message.answer(text=msg_finally, reply_markup=kb)
        return  # Завершення подальшої обробки

    with Session() as db:
        validator_name = VocabNameValidator(name=vocab_name, user_id=user_id, db_session=db)

    # Якщо назва словника коректна
    if validator_name.is_valid():
        msg_finally: str = create_vocab_message(vocab_name=vocab_name, content=MSG_SUCCESS_VOCAB_NAME_CREATED)

        kb: InlineKeyboardMarkup = get_kb_create_vocab_note()  # Клавіатура для створення примітки

        await state.update_data(vocab_name=vocab_name)  # Збереження назви словника в кеш FSM
        logging.info(f'Назва словника "{vocab_name}" збережена у FSM-кеш')

        fsm_state: State = VocabCreation.waiting_for_vocab_note  # FSM стан очікування примітки до словника
        await state.set_state(fsm_state)  # Переведення у новий FSM стан

        logging.info(f'FSM стан змінено на "{fsm_state}"')
    else:
        formatted_errors: str = validator_name.format_errors()
        msg_finally: str = create_vocab_message(vocab_name=vocab_name_old,
                                                content=MSG_VOCAB_NAME_ERRORS.format(vocab_name=vocab_name,
                                                                                     errors=formatted_errors))
    await message.answer(text=msg_finally, reply_markup=kb)


@router.message(VocabCreation.waiting_for_vocab_note)
async def process_vocab_note(message: Message, state: FSMContext) -> None:
    """Обробляє примітку до словника, яку ввів користувач"""
    data_fsm: dict = await state.get_data()  # Дані з FSM

    vocab_name: Any | None = data_fsm.get('vocab_name')
    vocab_note: str = message.text.strip()  # Примітка до словника, введена користувачем (без зайвих пробілів)

    kb: InlineKeyboardMarkup = get_kb_create_vocab_note()  # Клавіатура для створення примітки

    logging.info(f'Користувач ввів примітку "{vocab_note}" до словника "{vocab_name}"')

    validator_note = VocabNoteValidator(note=vocab_note)

    # Якщо примітка коректна
    if validator_note.is_valid():
        msg_finally: str = create_vocab_message(vocab_name=vocab_name,
                                                vocab_note=vocab_note,
                                                content=MSG_VOCAB_WORDPAIRS_SAVED_INSTRUCTIONS)

        await state.update_data(vocab_note=vocab_note)  # Збереження примітки в кеш FSM
        logging.info(f'Примітка "{vocab_note}" до словника "{vocab_name}" збережена у FSM-кеш')

        fsm_state: State = VocabCreation.waiting_for_wordpairs  # FSM стан очікування словникових пар
        await state.set_state(fsm_state)  # Переведення у новий FSM стан
        logging.info(f'FSM стан змінено на "{fsm_state}"')
    else:
        formatted_errors: str = validator_note.format_errors()  # Відформатований список помилок
        msg_finally: str = create_vocab_message(vocab_name=vocab_name,
                                                content=MSG_VOCAB_NOTE_ERRORS.format(vocab_note=vocab_note,
                                                                                     vocab_name=vocab_name,
                                                                                     errors=formatted_errors))
    await message.answer(text=msg_finally, reply_markup=kb)


@router.message(VocabCreation.waiting_for_wordpairs)
async def process_wordpairs(message: Message, state: FSMContext) -> None:
    """Обробляє словникові пари, введені користувачем"""
    data_fsm: dict = await state.get_data()

    vocab_name: str = data_fsm.get('vocab_name')

    wordpairs: str = message.text.strip()  # Словникові пари, введенні користувачем  (без зайвих пробілів)
    logging.info(f'Введено словникові пари "{wordpairs}" до словника "{vocab_name}"')

    wordpairs_lst: list[str] = wordpairs.split('\n')  # Список словникових пар

    valid_wordpairs_lst: list[str] = []  # Список коректних словникових пар
    invalid_wordpairs_lst: list[dict] = []  # Список не коректних словникових пар

    validated_data_wordpair: list = []  # Всі дані коректних словникових пар

    kb: InlineKeyboardMarkup = get_kb_create_wordpairs()  # Клавіатура для створення словникових пар

    for wordpair in wordpairs_lst:
        validator_wordpair = WordPairValidator(wordpair=wordpair, vocab_name=vocab_name)
        is_valid_wordpair: bool = validator_wordpair.is_valid()  # Чи коректна словникова пара

        if is_valid_wordpair:
            valid_wordpairs_lst.append(wordpair)

            validated_data: dict = validator_wordpair.validated_data  # Словник з даними словникової пари
            validated_data_wordpair.append(validated_data)
        else:
            formatted_errors: str = validator_wordpair.format_errors()
            invalid_wordpairs_lst.append({
                'wordpair': wordpair,
                'errors': formatted_errors
            })

    # Формуємо повідомлення для валідних словникових пар
    if valid_wordpairs_lst:
        valid_msg = "✅ Додані словникові пари:\n" + "\n".join([f"- {wp}" for wp in valid_wordpairs_lst])
    else:
        valid_msg = "⚠️ Немає валідних словникових пар."

    # Формуємо повідомлення для невалідних словникових пар
    if invalid_wordpairs_lst:
        invalid_msg_parts = [
            f"- {invalid['wordpair']}:\n{invalid['errors']}"
            for invalid in invalid_wordpairs_lst
        ]
        invalid_msg = "❌ Не додані словникові пари:\n" + "\n".join(invalid_msg_parts)
    else:
        invalid_msg = "🎉 Немає помилок серед введених пар!"

    # Загальне повідомлення з результатами перевірки
    final_message = f"{valid_msg}\n\n{invalid_msg}"

    # Відправляємо повідомлення користувачеві
    await message.answer(text=final_message, reply_markup=kb)


@router.callback_query(F.data == 'change_vocab_name')
async def process_change_vocab_name(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Змінити назву словника" під час створення словника.
    Переводить стан FSM у очікування назви словника.
    """
    logging.info('Користувач натиснув на кнопку "Змінити назву словника" при його створенні')

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника

    msg_finally: str = create_vocab_message(vocab_name=vocab_name, content=MSG_ENTER_NEW_VOCAB_NAME)

    # Клавіатура для створення назви словника з кнопкою "Залишити поточну назву"
    kb: InlineKeyboardMarkup = get_kb_create_vocab_name(is_keep_old_vocab_name=True)

    fsm_state: State = VocabCreation.waiting_for_vocab_name  # FSM стан очікування назви

    await callback.message.edit_text(text=msg_finally, reply_markup=kb)

    await state.set_state(fsm_state)  # Стан очікування назви словника
    logging.debug(f'FSM стан змінено на "{fsm_state}"')


@router.callback_query(F.data == 'keep_old_vocab_name')
async def process_keep_old_vocab_name(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Залишити поточну назву" під час зміни назви словника.
    Залишає поточну назву та переводить стан FSM у очікування примітки до словника.
    """
    logging.info('Користувач натиснув на кнопку "Залишити поточну назву" '
                 'під час зміни назви словника.')

    kb: InlineKeyboardMarkup = get_kb_create_vocab_note()  # Клавіатура для примітки

    data_fsm: Dict[str, Any] = await state.get_data()  # Отримання дані з FSM
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника
    msg_finally: str = create_vocab_message(vocab_name=vocab_name, content=MSG_ENTER_NEW_VOCAB_NAME)

    await callback.message.edit_text(text=msg_finally, reply_markup=kb)
    await state.set_state(VocabCreation.waiting_for_vocab_note)  # Стан очікування примітки до словника

    logging.debug(f'FSM стан змінено на {VocabCreation.waiting_for_vocab_note}.')


@router.callback_query(F.data.startswith('cancel_create_from_'))
async def process_cancel_create(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Скасувати" на всіх етапах створення словника.
    Залишає поточну назву та переводить стан FSM у очікування.
    """
    stage: str = callback.data.split('cancel_create_from_')[1]  # Процес, з якого було натиснута кнопка "Скасувати"

    logging.info(f'Була натиснута кнопка "Скасувати" при створенні словника, на етапі "{stage}"')

    finally_msg = 'Ви дійсно хочете скасувати створення словника?'

    await state.set_state()  # FSM у очікування

    logging.info('FSM стан переведено у очікування')

    kb: InlineKeyboardMarkup = get_kb_confirm_cancel(previous_stage=stage)  # Клавіатура для підтвердження
    await callback.message.edit_text(text=finally_msg, reply_markup=kb)


@router.callback_query(F.data.startswith('skip_creation_note'))
async def process_skip_creation_note(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Ні" у підтвердженні скасуванні створення словника.
    Прибирає примітку до словника.
    Переводить стан FSM у очікування словникових пар.
    """
    logging.info(f'Користувач {callback.from_user.id} натиснув на кнопку "Пропустити" '
                 'під час створення примітки до словника.')

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника
    vocab_note = DEFAULT_VOCAB_NOTE
    await state.update_data(vocab_note=vocab_note)  # Збереження примітки до словника в кеш FSM

    msg_vocab_note: str = f'Назва словника: {vocab_name}\nПримітка до словника: {vocab_note}\n\nВідправте словникові пари для цього словника у форматі:\n_word1, word2 : translation1, translation2 : annotation_\n- word2, translation2 та annotation — необов\'язкові поля.'
    kb: InlineKeyboardMarkup = get_kb_create_wordpairs()  # Клавіатура для введення назви
    await state.set_state(VocabCreation.waiting_for_wordpairs)

    await callback.message.edit_text(text=msg_vocab_note, reply_markup=kb)


@router.callback_query(F.data.startswith('back_to_'))
async def process_back_to(callback: CallbackQuery, state: FSMContext) -> None:
    """Обробляє натискання на кнопку 'Ні' та повертає користувача до процесу з якого натиснув кнопку 'Скасувати'"""
    stage: str = callback.data.split('back_to_')[1]  # Процес, з якого було натиснута кнопка "Скасувати
    logging.info(
        f'Користувач натиснув на кнопку "Ні" при підтвердженні скасування створення словника у процесі {state}')

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM

    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника
    vocab_note: Any | None = data_fsm.get('vocab_note')  # Примітка до словника

    if stage == 'vocab_name':
        # Процес введення назви словника
        msg_vocab_name: str = create_vocab_message(content=MSG_ENTER_VOCAB_NAME)

        kb: InlineKeyboardMarkup = get_kb_create_vocab_name()
        fsm_state: State = VocabCreation.waiting_for_vocab_name  # FSM стан очікування назви

        await callback.message.edit_text(text=msg_vocab_name, reply_markup=kb)
        await state.set_state(fsm_state)  # Переведення у новий FSM стан

        logging.info(f'FSM стан змінено на "{fsm_state}"')
    elif stage == 'vocab_note':
        # Процес введення примітки до словника
        msg_finally: str = create_vocab_message(vocab_name=vocab_name, content=MSG_SUCCESS_VOCAB_NAME_CREATED)
        kb: InlineKeyboardMarkup = get_kb_create_vocab_note()

        fsm_state = VocabCreation.waiting_for_vocab_note

        await callback.message.edit_text(text=msg_finally, reply_markup=kb)
        await state.set_state(fsm_state)

        logging.info(f'FSM стан змінено на "{fsm_state}"')
    elif stage == 'wordpairs':
        # Процес введення примітки до словника
        kb: InlineKeyboardMarkup = get_kb_create_wordpairs()
        msg_finally: str = create_vocab_message(vocab_name=vocab_name, content=MSG_VOCAB_WORDPAIRS_SAVED_INSTRUCTIONS)

        fsm_state = VocabCreation.waiting_for_wordpairs

        await callback.message.edit_text(text=msg_finally, reply_markup=kb)
        await state.set_state(fsm_state)

        logging.debug(f'FSM стан змінено на {fsm_state}.')
