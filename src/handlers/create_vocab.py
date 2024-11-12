import logging
from typing import Any

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from config import WORDPAIR_SEPARATOR
from db.models import User
from src.exceptions import UserNotFoundError
from db import crud
from db.database import Session
from src.fsm.states import VocabCreation
from src.keyboards.create_vocab_kb import (
    get_inline_kb_confirm_cancel,
    get_inline_kb_create_vocab_description,
    get_inline_kb_create_vocab_name,
    get_inline_kb_create_wordpairs,
)
from src.keyboards.menu_kb import get_inline_kb_menu
from src.keyboards.vocab_base_kb import get_inline_kb_vocab_buttons
from src.validators.vocab.vocab_description_validator import VocabDescriptionValidator
from src.validators.vocab.vocab_name_validator import VocabNameValidator
from src.validators.wordpair.wordpair_validator import WordpairValidator
from text_data import (
    MSG_CONFIRM_CANCEL_CREATE_VOCAB,
    MSG_ENTER_NEW_VOCAB_NAME,
    MSG_ENTER_VOCAB,
    MSG_ENTER_VOCAB_DESCRIPTION,
    MSG_ENTER_VOCAB_NAME,
    MSG_ENTER_WORDPAIRS,
    MSG_ENTER_WORDPAIRS_SMALL_INSTRUCTIONS,
    MSG_ERROR_VOCAB_BASE_EMPTY,
    MSG_ERROR_VOCAB_DESCRIPTION_INVALID,
    MSG_ERROR_VOCAB_NAME_DUPLICATE,
    MSG_ERROR_VOCAB_NAME_INVALID,
    MSG_ERROR_WORDPAIRS_NO_ADDED,
    MSG_ERROR_WORDPAIRS_NO_VALID,
    MSG_INFO_ADDED_WORDPAIRS,
    MSG_INFO_NO_ADDED_WORDPAIRS,
    MSG_SUCCESS_ALL_WORDPAIRS_VALID,
    MSG_SUCCESS_VOCAB_SAVED_TO_DB,
    MSG_TITLE_MENU,
)
from tools import fsm_utils, vocab_utils, wordpair_utils
from tools.message_formatter import add_vocab_data_to_message

logger: logging.Logger = logging.getLogger(__name__)
router = Router(name='create_vocab')


@router.callback_query(F.data == 'create_vocab')
async def process_create_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Додати словник" для створення нового словника"""
    logger.info(f'[START] Створення словника. USER_ID: {callback.from_user.id}')

    await state.clear()
    logger.info('FSM стан та FSM-Cache очищено')

    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()
    msg_text: str = add_vocab_data_to_message(message_text=MSG_ENTER_VOCAB_NAME)

    await fsm_utils.save_current_fsm_state(state, new_state=VocabCreation.waiting_for_vocab_name)
    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.message(VocabCreation.waiting_for_vocab_name)
async def process_create_vocab_name(message: types.Message, state: FSMContext) -> None:
    """Обробляє назву словника, введену користувач"""
    data_fsm: dict[str, Any] = await state.get_data()

    vocab_name: str = message.text.strip()
    vocab_name_old: str | None = data_fsm.get('vocab_name')  # Поточна назва словника (якщо є)

    logger.info(f'Користувач ввів назву словника: {vocab_name}')

    if vocab_utils.check_vocab_name_duplicate(vocab_name, vocab_name_old):
        logger.warning('Назва словника збігається з поточною')
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name(is_keep_old_vocab_name=True)
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                  message_text=MSG_ERROR_VOCAB_NAME_DUPLICATE)
        await message.answer(text=msg_text, reply_markup=kb)
        return  # Завершення обробки, якщо назва збігається

    with Session() as session:
        validator_vocab_name = VocabNameValidator(name=vocab_name,
                                                  user_id=message.from_user.id,
                                                  db_session=session)

    if validator_vocab_name.is_valid():
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_description()
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                  message_text=MSG_ENTER_VOCAB_DESCRIPTION)

        await state.update_data(vocab_name=vocab_name)
        logger.info('Назва словника збережена у FSM-Cache')

        await fsm_utils.save_current_fsm_state(state, new_state=VocabCreation.waiting_for_vocab_description)
    else:
        formatted_vocab_name_errors: str = validator_vocab_name.format_errors()

        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name_old,
                                                  message_text=MSG_ERROR_VOCAB_NAME_INVALID.format(
                                                      vocab_name=vocab_name,
                                                      errors=formatted_vocab_name_errors))
    await message.answer(text=msg_text, reply_markup=kb)


@router.callback_query(F.data == 'change_vocab_name')
async def process_change_vocab_name(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Змінити назву словника" під час створення словника"""
    logger.info('Користувач натиснув на кнопку "Змінити назву словника" при його створенні')

    data_fsm: dict[str, Any] = await state.get_data()
    vocab_name: str | None = data_fsm.get('vocab_name')

    msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                              message_text=MSG_ENTER_NEW_VOCAB_NAME)

    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name(is_keep_old_vocab_name=True)

    await fsm_utils.save_current_fsm_state(state, new_state=VocabCreation.waiting_for_vocab_name)
    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.callback_query(F.data == 'skip_create_vocab_description')
async def process_skip_create_vocab_description(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Пропустити" під час створення примітки до словника"""
    logger.info('Користувач натиснув на кнопку "Пропустити" під час створення примітки до словника')

    data_fsm: dict[str, Any] = await state.get_data()
    vocab_name: str | None = data_fsm.get('vocab_name')

    kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs(is_keep_status=False)
    msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                              message_text=MSG_ENTER_WORDPAIRS)

    await fsm_utils.save_current_fsm_state(state, new_state=VocabCreation.waiting_for_wordpairs)
    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.callback_query(F.data == 'keep_old_vocab_name')
async def process_keep_old_vocab_name(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Залишити поточну назву" під час створення словника"""
    logger.info('Користувач натиснув на кнопку "Залишити поточну назву" під час зміни назви словника')

    data_fsm: dict[str, Any] = await state.get_data()
    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_description()

    vocab_name: str | None = data_fsm.get('vocab_name')

    msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name, message_text=MSG_ENTER_VOCAB_NAME)

    await fsm_utils.save_current_fsm_state(state, new_state=VocabCreation.waiting_for_vocab_description)

    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.message(VocabCreation.waiting_for_vocab_description)
async def process_create_vocab_description(message: types.Message, state: FSMContext) -> None:
    """Обробляє опис словника, введений користувачем"""
    data_fsm: dict[str, Any] = await state.get_data()

    vocab_name: str | None = data_fsm.get('vocab_name')
    vocab_description: str = message.text.strip()

    logger.info(f'Користувач ввів опис словника: {vocab_description}')

    validator_description = VocabDescriptionValidator(description=vocab_description)
    if validator_description.is_valid():
        kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs(is_keep_status=False)
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                  vocab_description=vocab_description,
                                                  message_text=MSG_ENTER_WORDPAIRS)

        await state.update_data(vocab_description=vocab_description)
        logger.info('Опис словника збережений у FSM-Cache')

        await fsm_utils.save_current_fsm_state(state, new_state=VocabCreation.waiting_for_wordpairs)
    else:
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_description()
        formatted_vocab_description_errors: str = validator_description.format_errors()
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                  message_text=MSG_ERROR_VOCAB_DESCRIPTION_INVALID.format(
                                                      description=vocab_description,
                                                      vocab_name=vocab_name,
                                                      errors=formatted_vocab_description_errors))
    await message.answer(text=msg_text, reply_markup=kb)


@router.message(VocabCreation.waiting_for_wordpairs)
async def process_create_wordpairs(message: types.Message, state: FSMContext) -> None:
    """Обробляє словникові пари, введені користувачем"""
    data_fsm: dict[str, Any] = await state.get_data()

    vocab_name: str | None = data_fsm.get('vocab_name')
    vocab_description: str | None = data_fsm.get('vocab_description')

    wordpairs: str = message.text.strip()
    logger.info(f'Користувач ввів словникові пари: {wordpairs}')

    valid_wordpairs: list[str] = []  # Валідні словникові пари
    invalid_wordpairs: list[dict] = []  # Не валідні словникові пари та їх помилки

    kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs()

    for wordpair in wordpairs.split('\n'):
        validator_wordpair = WordpairValidator(wordpair)

        if validator_wordpair.is_valid():
            valid_wordpairs.append(wordpair)
        else:
            formatted_wordpair_errors: str = validator_wordpair.format_errors()
            invalid_wordpairs.append({
                'wordpair': wordpair,
                'errors': formatted_wordpair_errors})

    # Якщо є валідні словникові пари
    if len(valid_wordpairs) != 0:
        formatted_valid_wordpairs: str = wordpair_utils.format_valid_wordpairs(valid_wordpairs)
        valid_wordpairs_msg: str = MSG_INFO_ADDED_WORDPAIRS.format(wordpairs=formatted_valid_wordpairs)
        await fsm_utils.extend_valid_wordpairs_to_fsm_cache(state, wordpairs=valid_wordpairs)
    else:
        valid_wordpairs_msg = MSG_ERROR_WORDPAIRS_NO_VALID

    # Якщо є не валідні словникові пари
    if len(invalid_wordpairs) != 0:
        formatted_invalid_wordpairs: str = wordpair_utils.format_invalid_wordpairs(invalid_wordpairs)
        invalid_wordpairs_msg: str = MSG_INFO_NO_ADDED_WORDPAIRS.format(wordpairs=formatted_invalid_wordpairs)
        await fsm_utils.extend_invalid_wordpairs_to_fsm_cache(state, wordpairs=invalid_wordpairs)
    else:
        invalid_wordpairs_msg: str = MSG_SUCCESS_ALL_WORDPAIRS_VALID

    wordpairs_info_msg: str = '\n\n'.join((valid_wordpairs_msg,
                                           invalid_wordpairs_msg,
                                           MSG_ENTER_WORDPAIRS_SMALL_INSTRUCTIONS))

    msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                              vocab_description=vocab_description,
                                              message_text=wordpairs_info_msg)
    await message.answer(text=msg_text, reply_markup=kb)


@router.callback_query(F.data == 'create_wordpairs_status')
async def process_create_wordpairs_status(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Статус" під час введення словникових пар"""
    logger.info('Користувач натиснув на кнопку "Статус" під час введення словникових пар')

    data_fsm: dict[str, Any] = await state.get_data()

    vocab_name: str | None = data_fsm.get('vocab_name')
    vocab_description: str | None = data_fsm.get('vocab_description')

    kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs(is_keep_status=False)

    # Обробка валідних словникових пар
    all_valid_wordpairs: list[str] | None = data_fsm.get('all_valid_wordpairs')
    formatted_valid_wordpairs: str = wordpair_utils.format_valid_wordpairs(all_valid_wordpairs)
    valid_wordpairs_msg: str = MSG_INFO_ADDED_WORDPAIRS.format(wordpairs=formatted_valid_wordpairs)

    # Обробка не валідних словникових пар
    all_invalid_wordpairs: list[dict] | None = data_fsm.get('all_invalid_wordpairs')
    formatted_invalid_wordpairs: str = wordpair_utils.format_invalid_wordpairs(all_invalid_wordpairs)
    invalid_wordpairs_msg: str = MSG_INFO_NO_ADDED_WORDPAIRS.format(wordpairs=formatted_invalid_wordpairs)

    wordpairs_status_msg: str = '\n\n'.join((valid_wordpairs_msg,
                                             invalid_wordpairs_msg,
                                             MSG_ENTER_WORDPAIRS_SMALL_INSTRUCTIONS))

    msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                              vocab_description=vocab_description,
                                              message_text=wordpairs_status_msg)
    await callback.message.edit_text(text=msg_text, reply_markup=kb)

    # ! check_is_empty_valid_wordpairs
    """
    # Якщо немає доданих словникових пар
    if not validated_data_wordpairs:
        logger.info('Користувач не додав словникових пар')
        message_msg = f'Немає доданих словникових пар.\n\n{'MSG_VOCAB_WORDPAIRS_SAVED_SMALL_INSTRUCTIONS'}'
    else:
        formatted_wordpairs_lst: list = []

        for valid_data in validated_data_wordpairs:
            words_data_lst: list = valid_data['words']  # Список кортежів слів та їх анотацій
            translations_data_lst: list = valid_data['translations']  # Список кортежів перекладів та їх анотацій
            annotation: str = valid_data['annotation'] or '–'

            formatted_words: list[str] = ', '.join([f'{word} [{transcription or "–"}]' for
                                                    word, transcription in words_data_lst])
            formatted_translations: list[str] = ', '.join([f'{translation} [{transcription or "–"}]' for
                                                        translation, transcription in translations_data_lst])
            formatted_wordpair = f'{formatted_words} : {formatted_translations} : {annotation}'
            formatted_wordpairs_lst.append(formatted_wordpair)

        joined_wordpairs: str = '\n'.join([f'{num}. {i}' for num, i in enumerate(start=1,
                                                                                 iterable=formatted_wordpairs_lst)])

        message_msg: str = (
            f'Додані словникові пари:\n{joined_wordpairs}\n\n{'MSG_VOCAB_WORDPAIRS_SAVED_SMALL_INSTRUCTIONS'}')
    """


@router.callback_query(F.data == 'save_vocab')
async def process_save_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Зберегти" під час введення словникових пар"""
    logger.info('Користувач натиснув на кнопку "Зберегти" під час введення словникових пар')

    data_fsm: dict[str, Any] = await state.get_data()

    vocab_name: str | None = data_fsm.get('vocab_name')
    vocab_description: str | None = data_fsm.get('vocab_description')

    wordpairs: list[str] | None = data_fsm.get('all_valid_wordpairs')

    # Якщо немає валідних словникових пар
    if wordpairs is None:
        logger.warning('Немає доданих валідних словникових пар')
        msg_text: str = '\n\n'.join(('Немає доданих валідних словникових пар.',
                                     MSG_ENTER_WORDPAIRS_SMALL_INSTRUCTIONS))
        kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs(is_keep_status=False)
        await callback.message.edit_text(text=msg_text, reply_markup=kb)
        return  # Завершення обробки, якщо назва збігається

    await state.clear()  # Очищення FSM-кеш та FSM-стану
    logger.info('Очищення FSM стану')

    user_id: int = callback.from_user.id

    with Session() as db:
        user_vocabs: User | None = crud.get_user_vocab_by_user_id(db, user_id, is_all=True)  # Словники користувача

    # Клавіатура для відображення словників
    kb: InlineKeyboardMarkup = get_inline_kb_vocab_buttons(user_vocabs)

    msg_text: str = MSG_SUCCESS_VOCAB_SAVED_TO_DB.format(vocab_name=vocab_name,
                                                                  instruction=MSG_ENTER_VOCAB)

    # Список словників із розділеними компонентами словникової пари
    wordpair_components: list[dict] = [wordpair_utils.parse_wordpair_components(wordpair)
                                       for wordpair in wordpairs]

    try:
        with Session() as session:
            crud.add_vocab_to_db(session=session,
                                 user_id=user_id,
                                 vocab_name=vocab_name,
                                 vocab_description=vocab_description,
                                 wordpair_components=wordpair_components)
            logger.info(f'Був доданий до БД словник "{vocab_name}". Користувач: {user_id}')
    except UserNotFoundError as e:
        logger.error(e)
        return

    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.callback_query(F.data == 'cancel_create_vocab')
async def process_cancel_create_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Скасувати" при створенні словника.
    Відправляє клавіатуру для підтвердження скасування.
    """
    data_fsm: dict[str, Any] = await state.get_data()
    current_stage: Any | None = data_fsm.get('current_stage')
    logger.info(f'Була натиснута кнопка "Скасувати" при створенні словника, на етапі "{current_stage}"')

    await state.set_state()
    logger.info('FSM стан переведено у очікування')

    kb: InlineKeyboardMarkup = get_inline_kb_confirm_cancel()

    await callback.message.edit_text(text=MSG_CONFIRM_CANCEL_CREATE_VOCAB, reply_markup=kb)


@router.callback_query(F.data == 'cancel_no')
async def process_back_to_previous_stage(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Ні" при скасуванні створення словника.
    Повертає користувача до попереднього етапу (на якому була натиснута кнопка "Скасувати").
    """
    data_fsm: dict[str, Any] = await state.get_data()
    previous_stage: Any | None = data_fsm.get('current_stage')

    logger.info('Користувач натиснув на кнопку "Ні" під час підтвердження скасування створення словника')
    logger.info(f'Повернення на етап "{previous_stage}"')

    await state.set_state(previous_stage)
    logger.info(f'FSM стан змінено на "{previous_stage}"')

    vocab_name: str | None = data_fsm.get('vocab_name')
    vocab_description: str | None = data_fsm.get('vocab_description')

    if previous_stage == VocabCreation.waiting_for_vocab_name:
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()
        msg_text: str = add_vocab_data_to_message(vocab_name, vocab_description, MSG_ENTER_VOCAB_NAME)

    elif previous_stage == VocabCreation.waiting_for_vocab_description:
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_description()
        msg_text: str = add_vocab_data_to_message(vocab_name, vocab_description, MSG_ENTER_VOCAB_DESCRIPTION)

    elif previous_stage == VocabCreation.waiting_for_wordpairs:
        kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs()
        msg_text: str = add_vocab_data_to_message(vocab_name, vocab_description, MSG_ENTER_WORDPAIRS)

    await callback.message.edit_text(text=msg_text, reply_markup=kb)
