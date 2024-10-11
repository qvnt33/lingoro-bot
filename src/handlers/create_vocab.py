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
from config import (
    DEFAULT_VOCAB_NOTE,
    MAX_LENGTH_VOCAB_NAME,
    MAX_LENGTH_VOCAB_NOTE,
    MIN_LENGTH_VOCAB_NAME,
    MIN_LENGTH_VOCAB_NOTE,
    VOCAB_PAGINATION_LIMIT,
    MAX_COUNT_WORDS_WORDPAIR,
    MAX_COUNT_TRANSLATIONS_WORDPAIR,
    MAX_LENGTH_WORD_WORDPAIR,
    MAX_LENGTH_TRANSLATION_WORDPAIR
)
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
from src.validators.wordpair_validator import WordPairValidator

# from tools.escape_markdown import escape_markdown
from tools.read_data import app_data
from tools.message_formatter import format_message


router = Router(name='create_vocab')


@router.callback_query(F.data == 'create_vocab')
async def process_create_vocab(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Додати новий словник".
    Виконується процес створення словника.
    """
    user_id: int = callback.message.from_user.id

    log_text: str = app_data['logging']['info']['vocab']['create'].format(user_id=user_id)
    logging.info(log_text)

    kb: InlineKeyboardMarkup = get_kb_create_vocab_name()   # Клавіатура для створення назви словника

    msg_enter_vocab_name: str = app_data['prompts']['vocab']['enter_name']

    await callback.message.edit_text(text=msg_enter_vocab_name, reply_markup=kb)

    fsm_state: State = VocabCreation.waiting_for_vocab_name  # FSM стан очікування назви
    await state.set_state(fsm_state)  # Переведення у новий FSM стан

    log_text: str = app_data['logging']['debug']['fsm']['changed'].format(fsm_state=fsm_state)
    logging.debug(log_text)


@router.message(VocabCreation.waiting_for_vocab_name)
async def process_vocab_name(message: Message, state: FSMContext) -> None:
    """Обробляє назву словника, яку ввів користувач.
    Перевіряє введену назву.
    """
    user_id: int = message.from_user.id
    vocab_name: str = message.text.strip()  # Назва словника

    log_text: str = app_data['logging']['info']['vocab']['name']['entered'].format(name=vocab_name)
    logging.info(log_text)

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM
    vocab_name_old: Any | None = data_fsm.get('vocab_name')  # Стара назва словника

    kb: InlineKeyboardMarkup = get_kb_create_vocab_name()  # Клавіатура для створення примітки

    is_vocab_name_existing: bool = vocab_name_old is not None  # У словника вже є назва

    # Якщо введена назва словника збігається з поточною
    if is_vocab_name_existing and vocab_name.lower() == vocab_name_old.lower():
        log_text: str = app_data['logging']['vocab']['name']['name_exists'].format(name=vocab_name)
        logging.warning(log_text)

        # Клавіатура для введення або зміни назви словника
        kb: InlineKeyboardMarkup = get_kb_create_vocab_name(is_keep_old_vocab_name=True)

        # Повідомлення, що назва словника не може збігатися з поточною
        msg_vocab_same_name: str = app_data['info']['vocab']['name']['same_name']
        msg_vocab_name: str = format_message(vocab_name=vocab_name_old,
                                             content=msg_vocab_same_name)

        await message.answer(msg_vocab_name, reply_markup=kb)
        return  # Завершення подальшої обробки

    with Session() as db:
        # Валідатор для перевірки
        validator = VocabNameValidator(
            name=vocab_name,
            user_id=user_id,
            db_session=db)

    # Якщо назва словника коректна
    if validator.is_valid():
        log_text: str = app_data['logging']['info']['vocab']['name']['passed_test'].format(name=vocab_name)
        logging.info(log_text)

        # Повідомлення про успішне збереження назви словника
        msg_vocab_name_created: str = app_data['success']['vocab']['name']['created']
        msg_vocab_name: str = format_message(vocab_name=vocab_name,
                                             content=msg_vocab_name_created)

        kb: InlineKeyboardMarkup = get_kb_create_vocab_note()  # Клавіатура для створення примітки

        await state.update_data(vocab_name=vocab_name)  # Збереження назви в кеш FSM
        log_text: str = app_data['logging']['debug']['fsm']['vocab']['name_saved'].format(name=vocab_name)
        logging.info(log_text)

        fsm_state: State = VocabCreation.waiting_for_vocab_note  # FSM стан очікування примітки до словника
        await state.set_state(fsm_state)  # Переведення у новий FSM стан

        log_text: str = app_data['logging']['debug']['fsm']['changed'].format(fsm_state=fsm_state)
        logging.debug(log_text)
    else:
        formatted_errors: str = validator.format_errors()  # Відформатований список помилок

        # Текст з помилкам введеної назви словника
        list_of_errors: str = app_data['errors']['vocab']['name']['list_of_errors'].format(vocab_name=vocab_name,
                                                                                           list_of_errors=formatted_errors)
        # Повідомлення з заголовком старої назви
        msg_vocab_name: str = format_message(vocab_name=vocab_name_old,
                                             content=list_of_errors)

    await message.answer(text=msg_vocab_name, reply_markup=kb)


@router.message(VocabCreation.waiting_for_vocab_note)
async def process_vocab_note(message: Message, state: FSMContext) -> None:
    """Обробляє примітку до словника, яку ввів користувач.
    Переходить до процесу додавання словникових пар, якщо примітка коректна.
    """
    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника

    vocab_note: str = message.text  # Примітка до словника, введена користувачем

    kb: InlineKeyboardMarkup = get_kb_create_vocab_note()  # Клавіатура для створення примітки

    log_text: str = app_data['logging']['info']['vocab']['note']['entered'].format(note=vocab_name,
                                                                                   vocab_name=vocab_name)
    logging.info(log_text)

    # Валідатор для перевірки примітки до словника
    validator = VocabNoteValidator(note=vocab_note,
                                   vocab_name=vocab_name,
                                   min_len=MIN_LENGTH_VOCAB_NOTE,
                                   max_len=MAX_LENGTH_VOCAB_NOTE)

    # Якщо примітка коректна
    if validator.is_valid():
        log_text: str = app_data['logging']['info']['vocab']['note']['passed_test'].format(note=vocab_name,
                                                                                           vocab_name=vocab_name)
        logging.info(log_text)

        msg_vocab_note_created: str = app_data['success']['vocab']['note']['created']
        msg_vocab_note: str = format_message(vocab_name=vocab_name,
                                             content=msg_vocab_note_created)

        await state.update_data(vocab_note=vocab_note)  # Збереження примітки в кеш FSM
        log_text: str = app_data['logging']['debug']['fsm']['vocab']['name_saved'].format(name=vocab_name)
        logging.debug(log_text)

        fsm_state: State = VocabCreation.waiting_for_wordpairs  # FSM стан очікування словникових пар
        await state.set_state(fsm_state)  # Переведення у новий FSM стан

        log_text: str = app_data['logging']['debug']['fsm']['changed'].format(fsm_state=fsm_state)
        logging.debug(log_text)
    else:
        formatted_errors: str = validator.format_errors()  # Відформатований список помилок

        # Текст з помилкам введеної примітки до словника
        list_of_errors: str = app_data['errors']['vocab']['note']['list_of_errors'].format(vocab_note=vocab_note,
                                                                                           vocab_name=vocab_name,
                                                                                           list_of_errors=formatted_errors)
        msg_vocab_note: str = format_message(vocab_name=vocab_name,
                                             vocab_note=vocab_note,
                                             content=list_of_errors)
    await message.answer(text=msg_vocab_note, reply_markup=kb)


@router.message(VocabCreation.waiting_for_wordpairs)
async def process_wordpairs(message: Message, state: FSMContext) -> None:
    """Обробляє словникові пари, введені користувачем"""
    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника

    user_id: int = message.from_user.id
    wordpairs: str = message.text  # Введені користувачем словникові пари

    log_text: str = app_data['logging']['info']['vocab']['wordpair']['entered_all'].format(wordpairs=wordpairs,
                                                                                           vocab_name=vocab_name)
    logging.info(log_text)

    kb: InlineKeyboardMarkup = get_kb_create_wordpairs()  # Клавіатура для створення назви словника

    wordpairs_lst: list[str] = wordpairs.split('\n')  # Список всіх словникових пар

    valid_wordpairs_lst: list = []  # Валідні словникові пари
    invalid_wordpairs_lst: list = []  # Невалідні словникові пари

    for wordpair in wordpairs_lst:
        validator = WordPairValidator(wordpair=wordpair,
                                      user_id=user_id)

        # Якщо словникова пара валідна
        if validator.is_valid():
            wordpair_data: dict = validator.extract_data()  # Розділена словникова пара
            valid_wordpairs_lst.append(wordpair_data)  # Додавання до списку словникових пар


            log_text: str = app_data['logging']['info']['vocab']['wordpair']['passed_test'].format(wordpair=wordpair)
            logging.info(log_text)

            msg_vocab_note_created: str = app_data['success']['vocab']['note']['created']
            msg_vocab_note: str = format_message(vocab_name=vocab_name,
                                                content=msg_vocab_note_created)
        else:
            # Якщо є помилки, додаємо в список невалідну словникову пару та її помилку
            invalid_wordpairs_lst.append({
                'wordpair': wordpair,
                'errors': validator.format_errors()})

    # Якщо є невалідні словникові пари
    if len(invalid_wordpairs_lst) != 0:
        formatted_errors = '\n\n'.join([f'❌ Словникова пара: {pair["wordpair"]}\nПомилки:\n{pair["errors"]}'
                                        for pair in invalid_wordpairs_lst])
        msg_wordpairs = 'Є помилки у наступних парах:\n\n{formatted_errors}'
    else:
        # Обробка валідних пар
        msg_wordpairs = 'Всі словникові пари валідні!'

        # Можна тут додати логіку для збереження чи іншої обробки валідних пар
        for pair in valid_wordpairs_lst:
            words = ', '.join(pair['words'])
            translations = ', '.join(pair['translations'])
            annotation = pair['annotation'] or 'Без анотації'
            msg_wordpairs = 'Слова: {words}\nПереклади: {translations}\nАнотація: {annotation}'

    await message.answer(text=msg_wordpairs, reply_markup=kb)



@router.callback_query(F.data == 'change_vocab_name')
async def process_change_vocab_name(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Змінити назву словника" під час створення словника.
    Переводить стан FSM у очікування назви словника.
    """
    logging.info('Користувач натиснув на кнопку "Змінити назву словника" при його створенні.')

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника

    msg_content = 'Введіть, будь-ласка, нову назву словника або натисніть на кнопку "Залишити поточну назву".'
    msg_vocab_name: str = format_message(vocab_name=vocab_name, content=msg_content)

    # Клавіатура для створення назви словника з кнопкою "Залишити поточну назву"
    kb: InlineKeyboardMarkup = get_kb_create_vocab_name(is_keep_old_vocab_name=True)

    await callback.message.edit_text(text=msg_vocab_name, reply_markup=kb)

    await state.set_state(VocabCreation.waiting_for_vocab_name)  # Стан очікування назви словника
    logging.debug(f'FSM стан змінено на "{VocabCreation.waiting_for_vocab_name}".')


@router.callback_query(F.data == 'keep_old_vocab_name')
async def process_keep_old_vocab_name(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Залишити поточну назву" під час зміни назви словника.
    Залишає поточну назву та переводить стан FSM у очікування примітки до словника.
    """
    logging.info(f'Користувач {callback.from_user.id} натиснув на кнопку "Залишити поточну назву" '
                 'під час зміни назви словника.')

    kb: InlineKeyboardMarkup = get_kb_create_vocab_note()  # Клавіатура для примітки

    data_fsm: Dict[str, Any] = await state.get_data()  # Отримання дані з FSM
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника

    msg_vocab_note: str = f'Назва словника: {vocab_name}\n\nВведіть примітку до словника\n'
    'Якщо примітка до словника не потрібна - натисніть на кнопку "Пропустити".'

    await callback.message.edit_text(text=msg_vocab_note, reply_markup=kb)
    await state.set_state(VocabCreation.waiting_for_vocab_note)  # Стан очікування примітки до словника

    logging.debug(f'FSM стан змінено на {VocabCreation.waiting_for_vocab_note}.')


@router.callback_query(F.data.startswith('cancel_create_from_'))
async def process_cancel_create(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Скасувати" на всіх етапах створення словника.
    Залишає поточну назву та переводить стан FSM у очікування.
    """
    stage: str = callback.data.split('cancel_create_from_')[1]  # Процес, з якого було натиснута кнопка "Скасувати"

    logging.info(f'Була натиснута кнопка "Скасувати" при створенні словника, на етапі "{stage}".')

    msg_cancel_create = 'Ви дійсно хочете скасувати створення словника?'
    await state.set_state()  # FSM у очікування

    logging.debug('FSM стан переведено у очікування.')

    kb: InlineKeyboardMarkup = get_kb_confirm_cancel(previous_stage=stage)

    await callback.message.edit_text(text=msg_cancel_create, reply_markup=kb)


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


# Хендлер для натискання "Ні" при скасуванні
@router.callback_query(F.data.startswith('back_to_'))
async def process_back_to(callback: CallbackQuery, state: FSMContext) -> None:
    """Обробляє натискання на кнопку 'Ні' та повертає користувача до процесу з якого натиснув кнопку 'Скасувати'"""
    # Процес, з якого було натиснута кнопка "Скасувати"
    stage: str = callback.data.split('back_to_')[1]

    logging.info(f'Користувач "{callback.from_user.id}" натиснув на кнопку "Ні" та повертається до процесу "{stage}" з якого натиснув кнопку "Скасувати" '
                 'у підтвердженні скасуванні створення словника')

    data_fsm: Dict[str, Any] = await state.get_data()  # Отримання дані з FSM
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника
    vocab_note: Any | None = data_fsm.get('vocab_note')  # Назва словника
    if stage == 'vocab_name':
        # Процес введення назви словника
        kb: InlineKeyboardMarkup = get_kb_create_vocab_name()
        msg_vocab_name: str = 'Введіть назву словника:'

        await callback.message.edit_text(text=msg_vocab_name, reply_markup=kb)
        await state.set_state(VocabCreation.waiting_for_vocab_name)

        logging.debug(f'FSM стан змінено на {VocabCreation.waiting_for_vocab_name}.')
    elif stage == 'vocab_note':
        # Процес введення примітки до словника
        kb: InlineKeyboardMarkup = get_kb_create_vocab_note()
        msg_vocab_note: str = f'Назва словника: {vocab_name}\n\nВведіть примітку до словника\nЯкщо примітка до словника не потрібна - натисніть на кнопку "Пропустити".'

        await callback.message.edit_text(text=msg_vocab_note, reply_markup=kb)
        await state.set_state(VocabCreation.waiting_for_vocab_note)

        logging.debug(f'FSM стан змінено на {VocabCreation.waiting_for_vocab_note}.')
    elif stage == 'wordpairs':
        # Процес введення примітки до словника
        kb: InlineKeyboardMarkup = get_kb_create_wordpairs()
        msg_wordpairs: str = f'Назва словника: {vocab_name}\nПримітка до словника: {vocab_note}\n\nВідправте словникові пари для цього словника у форматі:\n_word1, word2 : translation1, translation2 : annotation_\n- word2, translation2 та annotation — необов\'язкові поля.'

        await callback.message.edit_text(text=msg_wordpairs, reply_markup=kb)
        await state.set_state(VocabCreation.waiting_for_wordpairs)

        logging.debug(f'FSM стан змінено на {VocabCreation.waiting_for_wordpairs}.')
