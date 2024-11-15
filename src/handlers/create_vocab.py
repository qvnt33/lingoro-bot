import logging
from typing import Any

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from db.crud import VocabCRUD
from db.database import Session
from exceptions import UserNotFoundError
from src.filters.check_empty_filters import CheckEmptyFilter
from src.fsm import states
from src.keyboards.create_vocab_kb import (
    get_inline_kb_confirm_cancel,
    get_inline_kb_create_vocab_description,
    get_inline_kb_create_vocab_name,
    get_inline_kb_create_wordpairs,
)
from src.keyboards.vocab_selection_kb import get_inline_kb_vocab_selection
from src.validators.vocab.vocab_description_validator import VocabDescriptionValidator
from src.validators.vocab.vocab_name_validator import VocabNameValidator
from src.validators.wordpair.wordpair_validator import WordpairValidator
from text_data import (
    MSG_CHOOSE_VOCAB,
    MSG_CONFIRM_CANCEL_CREATE_VOCAB,
    MSG_ENTER_NEW_VOCAB_NAME,
    MSG_ENTER_VOCAB_DESCRIPTION,
    MSG_ENTER_VOCAB_NAME,
    MSG_ENTER_WORDPAIRS,
    MSG_ENTER_WORDPAIRS_SMALL_INSTRUCTIONS,
    MSG_ERROR_NO_VALID_WORDPAIRS_ADDED,
    MSG_ERROR_VOCAB_DESCRIPTION_INVALID,
    MSG_ERROR_VOCAB_NAME_DUPLICATE,
    MSG_ERROR_VOCAB_NAME_INVALID,
    MSG_ERROR_WORDPAIRS_NO_VALID,
    MSG_INFO_ADDED_WORDPAIRS,
    MSG_INFO_NO_ADDED_WORDPAIRS,
    MSG_SUCCESS_ALL_WORDPAIRS_VALID,
    MSG_SUCCESS_VOCAB_SAVED_TO_DB,
)
from tools import fsm_utils, vocab_utils, wordpair_utils
from tools.message_formatter import add_vocab_data_to_message

router = Router(name='create_vocab')
logger: logging.Logger = logging.getLogger(__name__)


@router.callback_query(F.data == 'create_vocab')
async def process_create_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Додати словник".
    Запускає процес створення користувацького словника.
    """
    user_id: int = callback.from_user.id
    logger.info(f'[START] Створення користувацького словника. USER_ID: {user_id}')

    await state.clear()
    logger.info('FSM стан та FSM-Cache очищено')

    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()
    msg_enter_name: str = add_vocab_data_to_message(message_text=MSG_ENTER_VOCAB_NAME)

    await fsm_utils.save_current_fsm_state(state=state,
                                           new_state=states.VocabCreation.waiting_for_vocab_name)
    await callback.message.edit_text(text=msg_enter_name, reply_markup=kb)


@router.message(states.VocabCreation.waiting_for_vocab_name)
async def process_create_vocab_name(message: types.Message, state: FSMContext) -> None:
    """Обробляє назву користувацького словника, введену користувачем"""
    data_fsm: dict[str, Any] = await state.get_data()

    vocab_name: str = message.text.strip()
    vocab_name_old: str | None = data_fsm.get('vocab_name')  # Поточна назва користувацького словника (якщо є)

    logger.info(f'Введено назву користувацького словника: {vocab_name}')

    # Якщо введена назва збігається з поточною
    if vocab_utils.check_vocab_name_duplicate(vocab_name, vocab_name_old):
        logger.warning('Назва користувацького словника збігається з поточною')

        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name(is_keep_old_vocab_name=True)
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                  message_text=MSG_ERROR_VOCAB_NAME_DUPLICATE)

        await message.answer(text=msg_text, reply_markup=kb)
        return  # Завершення обробки

    user_id: int = message.from_user.id
    with Session() as session:
        validator_vocab_name = VocabNameValidator(vocab_name, user_id, session)

    if validator_vocab_name.is_valid():
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_description()
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                  message_text=MSG_ENTER_VOCAB_DESCRIPTION)

        await state.update_data(vocab_name=vocab_name)
        logger.info('Назва користувацького словника збережена у FSM-Cache')

        await fsm_utils.save_current_fsm_state(state=state,
                                               new_state=states.VocabCreation.waiting_for_vocab_description)
    else:
        formatted_vocab_name_errors: str = validator_vocab_name.format_errors()

        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()
        msg_error: str = MSG_ERROR_VOCAB_NAME_INVALID.format(vocab_name=vocab_name,
                                                             errors=formatted_vocab_name_errors)

        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name_old,
                                                  message_text=msg_error)
    await message.answer(text=msg_text, reply_markup=kb)


@router.callback_query(F.data == 'change_vocab_name')
async def process_change_vocab_name(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Змінити назву словника" під час створення користувацького словника.
    Переводить FSM стан в очікування введення нової назви користувацького словника.
    """
    logger.info('Натиснуто кнопку "Змінити назву словника" під час створення користувацького словника')

    data_fsm: dict[str, Any] = await state.get_data()
    vocab_name: str | None = data_fsm.get('vocab_name')

    msg_new_name: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                  message_text=MSG_ENTER_NEW_VOCAB_NAME)

    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name(is_keep_old_vocab_name=True)

    await fsm_utils.save_current_fsm_state(state=state,
                                           new_state=states.VocabCreation.waiting_for_vocab_name)
    await callback.message.edit_text(text=msg_new_name, reply_markup=kb)


@router.callback_query(F.data == 'skip_create_vocab_description')
async def process_skip_create_vocab_description(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Пропустити" під час створення опису користувацького словника.
    Переводить FSM стан в очікування введення словникових пар.
    """
    logger.info('Натиснуто на кнопку "Пропустити" під час створення опису користувацького словника')

    data_fsm: dict[str, Any] = await state.get_data()
    vocab_name: str | None = data_fsm.get('vocab_name')

    kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs(is_with_btn_status=False)
    msg_enter_wordpairs: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                         message_text=MSG_ENTER_WORDPAIRS)

    await fsm_utils.save_current_fsm_state(state=state,
                                           new_state=states.VocabCreation.waiting_for_wordpairs)
    await callback.message.edit_text(text=msg_enter_wordpairs, reply_markup=kb)


@router.callback_query(F.data == 'keep_old_vocab_name')
async def process_keep_old_vocab_name(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Залишити поточну назву" під час створення користувацького словника.
    Переводить FSM стан в очікування введення опису користувацького словника.
    """
    logger.info('Натиснуто на кнопку "Залишити поточну назву" під час зміни назви користувацького словника')

    data_fsm: dict[str, Any] = await state.get_data()
    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_description()

    vocab_name: str | None = data_fsm.get('vocab_name')

    msg_enter_name: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                    message_text=MSG_ENTER_VOCAB_NAME)

    await fsm_utils.save_current_fsm_state(state=state,
                                           new_state=states.VocabCreation.waiting_for_vocab_description)
    await callback.message.edit_text(text=msg_enter_name, reply_markup=kb)


@router.message(states.VocabCreation.waiting_for_vocab_description)
async def process_create_vocab_description(message: types.Message, state: FSMContext) -> None:
    """Обробляє опис користувацького словника, введений користувачем"""
    data_fsm: dict[str, Any] = await state.get_data()

    vocab_name: str | None = data_fsm.get('vocab_name')
    vocab_description: str = message.text.strip()

    logger.info(f'Введено опис користувацького словника: {vocab_description}')

    validator_vocab_description = VocabDescriptionValidator(description=vocab_description)
    if validator_vocab_description.is_valid():
        kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs(is_with_btn_status=False)
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                  vocab_description=vocab_description,
                                                  message_text=MSG_ENTER_WORDPAIRS)

        await state.update_data(vocab_description=vocab_description)
        logger.info('Опис користувацького словника збережений у FSM-Cache')

        await fsm_utils.save_current_fsm_state(state=state,
                                               new_state=states.VocabCreation.waiting_for_wordpairs)
    else:
        formatted_vocab_description_errors: str = validator_vocab_description.format_errors()

        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_description()
        msg_error: str = MSG_ERROR_VOCAB_DESCRIPTION_INVALID.format(description=vocab_description,
                                                                    vocab_name=vocab_name,
                                                                    errors=formatted_vocab_description_errors)

        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                  message_text=msg_error)
    await message.answer(text=msg_text, reply_markup=kb)


@router.message(states.VocabCreation.waiting_for_wordpairs)
async def process_create_wordpairs(message: types.Message, state: FSMContext) -> None:
    """Обробляє словникові пари, введені користувачем"""
    data_fsm: dict[str, Any] = await state.get_data()

    vocab_name: str | None = data_fsm.get('vocab_name')
    vocab_description: str | None = data_fsm.get('vocab_description')

    wordpairs: str = message.text.strip()
    logger.info(f'Введено словникові пари: {wordpairs}')

    valid_wordpairs: list[str] = []  # Валідні словникові пари
    invalid_wordpairs: list[dict] = []  # Не валідні словникові пари та їх помилки

    check_empty_filter = CheckEmptyFilter()

    kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs()

    for wordpair in wordpairs.split('\n'):
        validator_wordpair = WordpairValidator(wordpair)

        if validator_wordpair.is_valid():
            valid_wordpairs.append(wordpair)
        else:
            formatted_wordpair_errors: str = validator_wordpair.format_errors()
            invalid_wordpairs.append({'wordpair': wordpair,
                                      'errors': formatted_wordpair_errors})

    # Якщо є валідні словникові пари
    if not check_empty_filter.apply(valid_wordpairs):
        formatted_valid_wordpairs: str = wordpair_utils.format_valid_wordpairs(valid_wordpairs)
        valid_wordpairs_msg: str = MSG_INFO_ADDED_WORDPAIRS.format(wordpairs=formatted_valid_wordpairs)
        await fsm_utils.extend_valid_wordpairs_to_fsm_cache(state=state,
                                                            wordpairs=valid_wordpairs)
    else:
        valid_wordpairs_msg = MSG_ERROR_WORDPAIRS_NO_VALID

    # Якщо є не валідні словникові пари
    if not check_empty_filter.apply(invalid_wordpairs):
        formatted_invalid_wordpairs: str = wordpair_utils.format_invalid_wordpairs(invalid_wordpairs)
        invalid_wordpairs_msg: str = MSG_INFO_NO_ADDED_WORDPAIRS.format(wordpairs=formatted_invalid_wordpairs)
        await fsm_utils.extend_invalid_wordpairs_to_fsm_cache(state=state,
                                                              wordpairs=invalid_wordpairs)
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
    """Відстежує натискання на кнопку "Статус" під час введення словникових пар.
    Відправляє повідомлення з поточною статистикою доданих та не доданих словникових пар.
    """
    logger.info('Натиснуто на кнопку "Статус" під час введення словникових пар')

    data_fsm: dict[str, Any] = await state.get_data()

    vocab_name: str | None = data_fsm.get('vocab_name')
    vocab_description: str | None = data_fsm.get('vocab_description')

    kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs(is_with_btn_status=False)

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


@router.callback_query(F.data == 'save_vocab')
async def process_save_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Зберегти" під час введення словникових пар.
    Якщо є додані валідні словникові пари, то створює в БД користувацький словник з ними.
    """
    logger.info('Натиснуто на кнопку "Зберегти" під час введення словникових пар')

    data_fsm: dict[str, Any] = await state.get_data()

    vocab_name: str | None = data_fsm.get('vocab_name')
    vocab_description: str | None = data_fsm.get('vocab_description')
    wordpairs: list[str] | None = data_fsm.get('all_valid_wordpairs')

    check_empty_filter = CheckEmptyFilter()

    # Якщо немає валідних словникових пар
    if check_empty_filter.apply(wordpairs):
        logger.warning('Не було додано жодної валідної словникової пари')

        kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs(is_with_btn_status=False)
        msg_text: str = '\n\n'.join((MSG_ERROR_NO_VALID_WORDPAIRS_ADDED,
                                     MSG_ENTER_WORDPAIRS_SMALL_INSTRUCTIONS))

        await callback.message.edit_text(text=msg_text, reply_markup=kb)
        return  # Завершення обробки

    await state.clear()
    logger.info('FSM стан та FSM-Cache очищено')

    user_id: int = callback.from_user.id
    msg_text: str = MSG_SUCCESS_VOCAB_SAVED_TO_DB.format(vocab_name=vocab_name,
                                                         instruction=MSG_CHOOSE_VOCAB)

    # Список словникових пар із розділеними компонентами
    vocab_wordpairs: list[dict] = [wordpair_utils.parse_wordpair_components(wordpair)
                                   for wordpair in wordpairs]

    try:
        with Session() as session:
            vocab_crud = VocabCRUD(session)
            vocab_crud.create_new_vocab(user_id, vocab_name, vocab_description, vocab_wordpairs)

            logger.info(f'Був доданий до БД користувацький словник. Назва: {vocab_name}')
            logger.info(f'[END] Створення користувацького словника. USER_ID: {user_id}')

            # Дані всіх користувацьких словників користувача
            all_vocabs_data: list[dict] = vocab_crud.get_data_all_vocabs(user_id)
    except UserNotFoundError as e:
        logger.error(e)
        return

    kb: InlineKeyboardMarkup = get_inline_kb_vocab_selection(all_vocabs_data=all_vocabs_data,
                                                             callback_prefix='select_vocab_base')
    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.callback_query(F.data == 'cancel_create_vocab')
async def process_cancel_create_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Скасувати" при створенні користувацького словника.
    Відправляє клавіатуру для підтвердження скасування.
    """
    data_fsm: dict[str, Any] = await state.get_data()
    current_stage: State | None = data_fsm.get('current_stage')

    logger.info('Натиснуто на кнопку "Скасувати" під час створення користувацького словника. '
                f'На етапі "{current_stage}"')

    await state.set_state()
    logger.info('FSM стан переведено у очікування')

    kb: InlineKeyboardMarkup = get_inline_kb_confirm_cancel()
    msg_confirm_cancel_create = MSG_CONFIRM_CANCEL_CREATE_VOCAB

    await callback.message.edit_text(text=msg_confirm_cancel_create, reply_markup=kb)


@router.callback_query(F.data == 'cancel_create_vocab_no')
async def process_back_to_previous_stage(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Ні" при скасуванні створення користувацького словника.
    Повертає користувача до попереднього етапу (на якому була натиснута кнопка "Скасувати").
    """
    data_fsm: dict[str, Any] = await state.get_data()
    previous_stage: State | None = data_fsm.get('current_stage')

    logger.info('Натиснуто на кнопку "Ні" під час підтвердження скасування створення користувацького словника')
    logger.info(f'Повернення на етап "{previous_stage}"')

    await state.set_state(previous_stage)
    logger.info(f'FSM стан змінено на "{previous_stage}"')

    vocab_name: str | None = data_fsm.get('vocab_name')
    vocab_description: str | None = data_fsm.get('vocab_description')

    if previous_stage == states.VocabCreation.waiting_for_vocab_name:
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()
        msg_text: str = add_vocab_data_to_message(vocab_name, vocab_description, MSG_ENTER_VOCAB_NAME)

    elif previous_stage == states.VocabCreation.waiting_for_vocab_description:
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_description()
        msg_text: str = add_vocab_data_to_message(vocab_name, vocab_description, MSG_ENTER_VOCAB_DESCRIPTION)

    elif previous_stage == states.VocabCreation.waiting_for_wordpairs:
        kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs()
        msg_text: str = add_vocab_data_to_message(vocab_name, vocab_description, MSG_ENTER_WORDPAIRS)

    await callback.message.edit_text(text=msg_text, reply_markup=kb)
