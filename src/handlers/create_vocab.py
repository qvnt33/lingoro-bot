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

from tools.escape_markdown import escape_markdown
from tools.read_data import app_data

router = Router(name='create_vocab')


@router.callback_query(F.data == 'create_vocab')
async def process_create_vocab(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Додати новий словник".
    Виконується процес створення словника.
    """
    user_id: int = callback.message.id

    logging.info(f'Користувач "{user_id}" почав "процес створення словника".')

    kb: InlineKeyboardMarkup = get_kb_create_vocab_name()   # Клавіатура для створення назви словника
    await callback.message.edit_text(text='Введіть назву словника:',
                                     reply_markup=kb)

    # Переведення FSM у стан очікування назви словника
    await state.set_state(VocabCreation.waiting_for_vocab_name)
    logging.debug(f'FSM стан змінено на "{VocabCreation.waiting_for_vocab_name}".')


@router.message(VocabCreation.waiting_for_vocab_name)
async def process_vocab_name(message: Message, state: FSMContext) -> None:
    """Обробляє назву словника, яку ввів користувач.
    Проводиться перевірка введеної назви.
    """
    user_id: int = message.from_user.id  # ID користувача
    vocab_name: str = message.text  # Назва словника, введена користувачем

    logging.info(f'Користувач ввів назву словника: "{escape_markdown(vocab_name)}".')

    with Session() as db:
        # Валідатор для перевірки коректності назви
        validator = VocabNameValidator(
            vocab_name=vocab_name,
            user_id=user_id,
            min_length_name=MIN_LENGTH_VOCAB_NAME,
            max_length_name=MAX_LENGTH_VOCAB_NAME,
            db=db)

    # Якщо назва словника коректна
    if validator.is_valid():
        logging.info(f'Назва словника "{escape_markdown(vocab_name)}" пройшла всі перевірки.')

        kb: InlineKeyboardMarkup = get_kb_create_vocab_note()  # Клавіатура для створення примітки
        msg_vocab_name: str = f'*Назва словника:* {escape_markdown(vocab_name)}\n\n'
        'Введіть *примітку* до словника.\n'
        'Якщо примітка до словника не потрібна - натисніть на кнопку "Пропустити".'

        await state.update_data(vocab_name=vocab_name)  # Збереження назви в кеш FSM

        logging.debug('"Назва словника" збережена у кеш FSM.')

        await state.set_state(VocabCreation.waiting_for_vocab_note)  # Переведення FSM у стан очікування примітки

        logging.debug(f'FSM стан змінено на "{escape_markdown(VocabCreation.waiting_for_vocab_note)}".')
    else:
        kb: InlineKeyboardMarkup = get_kb_create_vocab_name()  # Клавіатура для введення назви

        formatted_errors: str = validator.format_errors()  # Відформатований список помилок
        msg_vocab_name: str = f'❌ *Є помилки у назві словника "{escape_markdown(vocab_name)}"*\n{formatted_errors}\n\n'

    await message.answer(text=msg_vocab_name,
                         reply_markup=kb)


@router.message(VocabCreation.waiting_for_vocab_note)
async def process_vocab_note(message: Message, state: FSMContext) -> None:
    """Обробляє примітку до словника, яку ввів користувач.
    Переходить до процесу додавання словникових пар, якщо примітка коректна.
    """
    kb: InlineKeyboardMarkup = get_kb_create_vocab_name()  # Клавіатура для створення примітки

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника

    vocab_note: str = message.text  # Примітка, введена користувачем

    logging.info(f'Користувач ввів примітку "{escape_markdown(vocab_note)}" до словника "{escape_markdown(vocab_name)}".')

    # Валідатор для перевірки примітки до словника
    validator = VocabNoteValidator(note=vocab_note,
                                   min_length_vocab_note=MIN_LENGTH_VOCAB_NOTE,
                                   max_length_vocab_note=MAX_LENGTH_VOCAB_NOTE)

    # Якщо примітка коректна
    if validator.is_valid():
        logging.info(f'Примітка "{escape_markdown(vocab_note)}" до словника "{escape_markdown(vocab_name)}" пройшла всі перевірки.')

        kb: InlineKeyboardMarkup = get_kb_create_wordpairs()  # Клавіатура для введення назви словника

        msg_vocab_note: str = f'Назва словника: "{escape_markdown(vocab_name)}"\n"'
        f'Примітка до словника:" {escape_markdown(vocab_note)}\n\n'
        'Відправте "словникові пари" для цього словника у форматі:\n'
        '_word1, word2 : translation1, translation2 : annotation_\n'
        '- "word2", "translation2" та "annotation" — необов\'язкові поля.'

        await state.update_data(vocab_note=vocab_note)  # Збереження примітки в кеш FSM

        logging.debug('"Примітка до словника" збережена у кеш FSM.')

        await state.set_state(VocabCreation.waiting_for_wordpairs)  # Переведення FSM у стан очікування словникових пар

        logging.debug(f'FSM стан змінено на "{VocabCreation.waiting_for_wordpairs}".')
    else:
        formatted_errors: str = validator.format_errors()  # Відформатований список помилок
        msg_vocab_note: str = f'❌ *Є помилки у примітці до словника:*\n{escape_markdown(formatted_errors)}\n\n'
        'Будь ласка, введіть іншу *примітку*.'
        '\nЯкщо примітка до словника не потрібна - натисніть на кнопку "*Пропустити*".'
    await message.answer(text=msg_vocab_note, reply_markup=kb)


@router.message(VocabCreation.waiting_for_wordpairs)
async def process_wordpairs(message: Message, state: FSMContext) -> None:
    """Обробляє словникові пари, введені користувачем"""
    wordpairs: str = message.text  # Введені користувачем словникові пари

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника

    logging.info(f'Користувач ввів словникові пари "{escape_markdown(wordpairs)}" до словника "{escape_markdown(vocab_name)}".')

    for wordpair in wordpairs:
        validator = WordPairValidator(wordpair=wordpair,
                                      max_count_words=MAX_COUNT_WORDS_WORDPAIR,
                                      max_count_translations=MAX_COUNT_TRANSLATIONS_WORDPAIR,
                                      max_len_word=MAX_LENGTH_WORD_WORDPAIR,
                                      max_len_translation=MAX_LENGTH_TRANSLATION_WORDPAIR)
        if validator.is_valid():
            logging.info(f'Словникова пара "{escape_markdown(wordpair)}" пройшла всі перевірки.')

            words = validator.words
            translations = validator.translations
            annotation = validator.annotation

        # Тут можна зберегти розділені дані в базу або кеш FSM
        await state.update_data(words=words, translations=translations, annotation=annotation)
        await message.answer('✅ Словникова пара додана успішно!')
    else:
        formatted_errors = validator.format_errors()
        await message.answer(f'❌ Є помилки у словниковій парі:\n{escape_markdown(formatted_errors)}\nСпробуйте ще раз.')


@router.callback_query(F.data == 'change_vocab_name')
async def process_change_vocab_name(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Змінити назву словника" під час створення словника.
    Переводить стан FSM у очікування назви словника.
    """
    logging.info('Користувач натиснув на кнопку "Змінити назву словника" при його створенні.')

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника

    # Клавіатура для створення назви словника з кнопкою "Залишити поточну назву"
    kb: InlineKeyboardMarkup = get_kb_create_vocab_name(is_keep_old_vocab_name=True)

    await callback.message.edit_text(text=f'*Поточна назва:* {vocab_name}\n\nВведіть іншу *назву* словника:', reply_markup=kb)
    await state.set_state(VocabCreation.waiting_for_vocab_name)  # Стан очікування назви словника

    logging.debug(f'FSM стан змінено на {VocabCreation.waiting_for_vocab_name}.')


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

    msg_vocab_note: str = f'*Назва словника:* {vocab_name}\n\nВведіть *примітку* до словника\n'
    'Якщо примітка до словника не потрібна - натисніть на кнопку "*Пропустити*".'

    await callback.message.edit_text(text=msg_vocab_note, reply_markup=kb)
    await state.set_state(VocabCreation.waiting_for_vocab_note)  # Стан очікування примітки до словника

    logging.debug(f'FSM стан змінено на {VocabCreation.waiting_for_vocab_note}.')


@router.callback_query(F.data.startswith('cancel_create_from_'))
async def process_cancel_create(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Скасувати" на всіх етапах створення словника.
    Залишає поточну назву та переводить стан FSM у очікування.
    """
    logging.info(f'Користувач {callback.from_user.id} натиснув на кнопку "Скасувати" '
                 'на одну із етапів створення словника.')

    # Процес, з якого було натиснута кнопка "Скасувати"
    stage: str = callback.data.split('cancel_create_from_')[1]
    logging.info(f'Користувач {callback.from_user.id} натиснув на кнопку "Скасувати" на етапі створення словника "{stage}".')
    msg_cancel_create = 'Ви дійсно хочете *скасувати* створення словника?'
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

    msg_vocab_note: str = f'*Назва словника:* {escape_markdown(vocab_name)}\n*Примітка до словника:* {escape_markdown(vocab_note)}\n\nВідправте *словникові пари* для цього словника у форматі:\n_word1, word2 : translation1, translation2 : annotation_\n- *word2*, *translation2* та *annotation* — необов\'язкові поля.'
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
        msg_vocab_name: str = 'Введіть *назву* словника:'

        await callback.message.edit_text(text=msg_vocab_name, reply_markup=kb)
        await state.set_state(VocabCreation.waiting_for_vocab_name)

        logging.debug(f'FSM стан змінено на {VocabCreation.waiting_for_vocab_name}.')
    elif stage == 'vocab_note':
        # Процес введення примітки до словника
        kb: InlineKeyboardMarkup = get_kb_create_vocab_note()
        msg_vocab_note: str = f'*Назва словника:* {vocab_name}\n\nВведіть *примітку* до словника\nЯкщо примітка до словника не потрібна - натисніть на кнопку "*Пропустити*".'

        await callback.message.edit_text(text=msg_vocab_note, reply_markup=kb)
        await state.set_state(VocabCreation.waiting_for_vocab_note)

        logging.debug(f'FSM стан змінено на {VocabCreation.waiting_for_vocab_note}.')
    elif stage == 'wordpairs':
        # Процес введення примітки до словника
        kb: InlineKeyboardMarkup = get_kb_create_wordpairs()
        msg_wordpairs: str = f'*Назва словника:* {escape_markdown(vocab_name)}\n*Примітка до словника:* {escape_markdown(vocab_note)}\n\nВідправте *словникові пари* для цього словника у форматі:\n_word1, word2 : translation1, translation2 : annotation_\n- *word2*, *translation2* та *annotation* — необов\'язкові поля.'

        await callback.message.edit_text(text=msg_wordpairs, reply_markup=kb)
        await state.set_state(VocabCreation.waiting_for_wordpairs)

        logging.debug(f'FSM стан змінено на {VocabCreation.waiting_for_wordpairs}.')
