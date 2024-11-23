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
    get_kb_confirm_cancel_create_vocab,
    get_kb_create_vocab_description,
    get_kb_create_vocab_name,
    get_kb_create_wordpairs,
)
from src.keyboards.vocab_base_kb import get_kb_vocab_selection_base
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
from tools.vocab_utils import add_vocab_data_to_message

router = Router(name='create_vocab')
logger: logging.Logger = logging.getLogger(__name__)


@router.callback_query(F.data == 'create_vocab')
async def process_create_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Додати словник".
    Запускає процес створення користувацького словника.
    """
    user_id: int = callback.from_user.id
    logger.info(f'Початок процесу "створення користувацького словника". USER_ID: {user_id}')

    await state.clear()
    logger.info('FSM стан та FSM-Cache очищено перед створенням користувацького словника')

    kb: InlineKeyboardMarkup = get_kb_create_vocab_name()
    msg_enter_name: str = add_vocab_data_to_message(message_text=MSG_ENTER_VOCAB_NAME)

    new_state: State = states.VocabCreation.waiting_for_vocab_name
    await fsm_utils.save_current_fsm_state(state, new_state)
    logger.info(f'FSM стан змінено на "{new_state}"')

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
        logger.warning('Назва користувацького словника збігається з поточною (не зважаючи на регістр)')

        kb: InlineKeyboardMarkup = get_kb_create_vocab_name(is_keep_old_vocab_name=True)
        msg_name_duplicate: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                            message_text=MSG_ERROR_VOCAB_NAME_DUPLICATE)

        await message.answer(text=msg_name_duplicate, reply_markup=kb)
        return  # Завершення обробки

    user_id: int = message.from_user.id
    with Session() as session:
        validator_vocab_name = VocabNameValidator(vocab_name, user_id, session)

    if validator_vocab_name.is_valid():
        kb: InlineKeyboardMarkup = get_kb_create_vocab_description()
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                  message_text=MSG_ENTER_VOCAB_DESCRIPTION)

        await state.update_data(vocab_name=vocab_name)
        logger.info('Назва користувацького словника збережена у FSM-Cache')

        new_state: State = states.VocabCreation.waiting_for_vocab_description
        await fsm_utils.save_current_fsm_state(state, new_state)
        logger.info(f'FSM стан змінено на "{new_state}"')
    else:
        formatted_vocab_name_errors: str = validator_vocab_name.format_errors()

        kb: InlineKeyboardMarkup = get_kb_create_vocab_name()
        msg_error_name_invalid: str = MSG_ERROR_VOCAB_NAME_INVALID.format(name=vocab_name,
                                                                          errors=formatted_vocab_name_errors)

        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name_old,
                                                  message_text=msg_error_name_invalid)
    await message.answer(text=msg_text, reply_markup=kb)


@router.callback_query(F.data == 'change_vocab_name')
async def process_change_vocab_name(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Змінити назву словника" під час створення користувацького словника.
    Переводить FSM стан в очікування введення нової назви користувацького словника.
    """
    logger.info('Обрано змінення назви користувацького словника під час його створення')

    data_fsm: dict[str, Any] = await state.get_data()

    kb: InlineKeyboardMarkup = get_kb_create_vocab_name(is_keep_old_vocab_name=True)

    vocab_name: str = data_fsm.get('vocab_name')
    msg_enter_new_name: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                        message_text=MSG_ENTER_NEW_VOCAB_NAME)

    new_state: State = states.VocabCreation.waiting_for_vocab_name
    await fsm_utils.save_current_fsm_state(state, new_state)
    logger.info(f'FSM стан змінено на "{new_state}"')

    await callback.message.edit_text(text=msg_enter_new_name, reply_markup=kb)


@router.callback_query(F.data == 'skip_create_vocab_description')
async def process_skip_create_vocab_description(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Пропустити" під час створення опису користувацького словника.
    Переводить FSM стан в очікування введення словникових пар.
    """
    logger.info('Обрано пропуск додавання опису користувацького словника під час створення користувацького словника')

    data_fsm: dict[str, Any] = await state.get_data()

    kb: InlineKeyboardMarkup = get_kb_create_wordpairs(is_with_btn_status=False)

    vocab_name: str = data_fsm.get('vocab_name')
    msg_enter_wordpairs: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                         message_text=MSG_ENTER_WORDPAIRS)

    new_state: State = states.VocabCreation.waiting_for_wordpairs
    await fsm_utils.save_current_fsm_state(state, new_state)
    logger.info(f'FSM стан змінено на "{new_state}"')

    await callback.message.edit_text(text=msg_enter_wordpairs, reply_markup=kb)


@router.callback_query(F.data == 'keep_old_vocab_name')
async def process_keep_old_vocab_name(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Залишити поточну назву" під час створення користувацького словника.
    Переводить FSM стан в очікування введення опису користувацького словника.
    """
    logger.info('Обрано залишити поточну назву під час зміни назви користувацького словника, створюючи його')

    data_fsm: dict[str, Any] = await state.get_data()

    kb: InlineKeyboardMarkup = get_kb_create_vocab_description()

    vocab_name: str = data_fsm.get('vocab_name')
    msg_enter_description: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                           message_text=MSG_ENTER_VOCAB_DESCRIPTION)

    new_state: State = states.VocabCreation.waiting_for_vocab_description
    await fsm_utils.save_current_fsm_state(state, new_state)
    logger.info(f'FSM стан змінено на "{new_state}"')

    await callback.message.edit_text(text=msg_enter_description, reply_markup=kb)


@router.message(states.VocabCreation.waiting_for_vocab_description)
async def process_create_vocab_description(message: types.Message, state: FSMContext) -> None:
    """Обробляє опис користувацького словника, введений користувачем"""
    data_fsm: dict[str, Any] = await state.get_data()

    vocab_name: str = data_fsm.get('vocab_name')
    vocab_description: str = message.text.strip()

    logger.info(f'Введено опис користувацького словника: {vocab_description}')

    validator_vocab_description = VocabDescriptionValidator(description=vocab_description)
    if validator_vocab_description.is_valid():
        kb: InlineKeyboardMarkup = get_kb_create_wordpairs(is_with_btn_status=False)
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                  vocab_description=vocab_description,
                                                  message_text=MSG_ENTER_WORDPAIRS)

        await state.update_data(vocab_description=vocab_description)
        logger.info('Опис користувацького словника збережений у FSM-Cache')

        new_state: State = states.VocabCreation.waiting_for_wordpairs
        await fsm_utils.save_current_fsm_state(state, new_state)
        logger.info(f'FSM стан змінено на "{new_state}"')
    else:
        formatted_vocab_description_errors: str = validator_vocab_description.format_errors()

        kb: InlineKeyboardMarkup = get_kb_create_vocab_description()
        msg_error: str = MSG_ERROR_VOCAB_DESCRIPTION_INVALID.format(description=vocab_description,
                                                                    name=vocab_name,
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
    logger.info(f'Введено словникові пари (одним повідомленням): {wordpairs}')

    valid_wordpairs: list[str] = []
    invalid_wordpairs: list[dict] = []

    check_empty_filter = CheckEmptyFilter()

    kb: InlineKeyboardMarkup = get_kb_create_wordpairs()

    for wordpair in wordpairs.split('\n'):
        validator_wordpair = WordpairValidator(wordpair)
        if validator_wordpair.is_valid():
            valid_wordpairs.append(wordpair)
            continue
        formatted_wordpair_errors: str = validator_wordpair.format_errors()
        invalid_wordpairs.append({'wordpair': wordpair,
                                  'errors': formatted_wordpair_errors})

    # Якщо є валідні словникові пари
    if not check_empty_filter.apply(valid_wordpairs):
        formatted_valid_wordpairs: str = wordpair_utils.format_valid_wordpairs(valid_wordpairs)
        valid_wordpairs_msg: str = MSG_INFO_ADDED_WORDPAIRS.format(wordpairs=formatted_valid_wordpairs)
        await fsm_utils.extend_valid_wordpairs_to_fsm_cache(valid_wordpairs, state)
    else:
        valid_wordpairs_msg = MSG_ERROR_WORDPAIRS_NO_VALID

    # Якщо є не валідні словникові пари
    if not check_empty_filter.apply(invalid_wordpairs):
        formatted_invalid_wordpairs: str = wordpair_utils.format_invalid_wordpairs(invalid_wordpairs)
        invalid_wordpairs_msg: str = MSG_INFO_NO_ADDED_WORDPAIRS.format(wordpairs=formatted_invalid_wordpairs)
        await fsm_utils.extend_invalid_wordpairs_to_fsm_cache(invalid_wordpairs, state)
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
    logger.info('Обрано показ статусу доданих словникових пар під час створення користувацького словника')

    data_fsm: dict[str, Any] = await state.get_data()

    vocab_name: str = data_fsm.get('vocab_name')
    vocab_description: str | None = data_fsm.get('vocab_description')

    kb: InlineKeyboardMarkup = get_kb_create_wordpairs(is_with_btn_status=False)

    # Обробка валідних словникових пар
    all_valid_wordpairs: list[str] | None = data_fsm.get('all_valid_wordpairs')
    formatted_valid_wordpairs: str = wordpair_utils.format_valid_wordpairs(all_valid_wordpairs)
    valid_wordpairs_msg: str = MSG_INFO_ADDED_WORDPAIRS.format(wordpairs=formatted_valid_wordpairs)

    # Обробка не валідних словникових пар
    all_invalid_wordpairs: list[dict] | None = data_fsm.get('all_invalid_wordpairs')
    formatted_invalid_wordpairs: str = wordpair_utils.format_invalid_wordpairs(all_invalid_wordpairs)
    invalid_wordpairs_msg: str = MSG_INFO_NO_ADDED_WORDPAIRS.format(wordpairs=formatted_invalid_wordpairs)

    msg_wordpairs_status: str = '\n\n'.join((valid_wordpairs_msg,
                                             invalid_wordpairs_msg,
                                             MSG_ENTER_WORDPAIRS_SMALL_INSTRUCTIONS))

    msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                              vocab_description=vocab_description,
                                              message_text=msg_wordpairs_status)
    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.callback_query(F.data == 'save_vocab')
async def process_save_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Зберегти" під час введення словникових пар.
    Якщо є додані валідні словникові пари, то створює в БД користувацький словник з ними.
    """
    logger.info('Обрано збереження користувацького словника під час його створення')

    data_fsm: dict[str, Any] = await state.get_data()

    vocab_name: str = data_fsm.get('vocab_name')
    vocab_description: str | None = data_fsm.get('vocab_description')
    wordpairs: list[str] | None = data_fsm.get('all_valid_wordpairs')

    # Якщо немає валідних словникових пар
    check_empty_filter = CheckEmptyFilter()
    if check_empty_filter.apply(wordpairs):
        logger.warning('Не було додано жодної валідної словникової пари. Не вдалося створити користувацький словник')

        kb: InlineKeyboardMarkup = get_kb_create_wordpairs(is_with_btn_save=False, is_with_btn_status=False)
        msg_error_with_instruction: str = '\n\n'.join((MSG_ERROR_NO_VALID_WORDPAIRS_ADDED,
                                                       MSG_ENTER_WORDPAIRS_SMALL_INSTRUCTIONS))

        await callback.message.edit_text(text=msg_error_with_instruction, reply_markup=kb)
        return  # Завершення обробки

    await state.clear()
    logger.info('FSM стан та FSM-Cache очищено після збереження користувацького словника')

    user_id: int = callback.from_user.id
    msg_vocab_saved_with_choose: str = '\n\n'.join((MSG_SUCCESS_VOCAB_SAVED_TO_DB.format(name=vocab_name),
                                                    MSG_CHOOSE_VOCAB))

    # Список словникових пар із розділеними компонентами
    vocab_wordpairs: list[dict] = [wordpair_utils.parse_wordpair_components(wordpair)
                                   for wordpair in wordpairs]

    try:
        with Session() as session:
            vocab_crud = VocabCRUD(session)
            vocab_crud.create_new_vocab(user_id, vocab_name, vocab_description, vocab_wordpairs)

            logger.info(f'До БД доданий користувацький словник. Назва: "{vocab_name}". USER_ID: {user_id}')

            # Дані всіх користувацьких словників користувача
            all_vocabs_data: list[dict] = vocab_crud.get_all_vocabs_data(user_id)
    except UserNotFoundError as e:
        logger.error(e)
        return

    kb: InlineKeyboardMarkup = get_kb_vocab_selection_base(all_vocabs_data[::-1])
    await callback.message.edit_text(text=msg_vocab_saved_with_choose, reply_markup=kb)


@router.callback_query(F.data == 'cancel_create_vocab')
async def process_cancel_create_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Скасувати" при створенні користувацького словника.
    Відправляє клавіатуру для підтвердження скасування.
    """
    data_fsm: dict[str, Any] = await state.get_data()
    current_stage: State | None = data_fsm.get('current_stage')

    logger.info('Обрано скасування створення користувацького словника під час його створення. '
                f'На етапі "{current_stage}"')

    await state.set_state()
    logger.info('FSM стан переведено у очікування')

    kb: InlineKeyboardMarkup = get_kb_confirm_cancel_create_vocab()
    msg_confirm_cancel_create: str = MSG_CONFIRM_CANCEL_CREATE_VOCAB

    await callback.message.edit_text(text=msg_confirm_cancel_create, reply_markup=kb)


@router.callback_query(F.data == 'cancel_create_vocab_no')
async def process_back_to_previous_stage(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Ні" при скасуванні створення користувацького словника.
    Повертає користувача до попереднього етапу (на якому була натиснута кнопка "Скасувати").
    """
    data_fsm: dict[str, Any] = await state.get_data()
    previous_stage: State | None = data_fsm.get('current_stage')

    logger.info('Продовжено створення користувацького словника')
    logger.info(f'Повернення на етап "{previous_stage}"')

    await state.set_state(previous_stage)
    logger.info(f'FSM стан змінено на "{previous_stage}"')

    vocab_name: str = data_fsm.get('vocab_name')
    vocab_description: str | None = data_fsm.get('vocab_description')

    if previous_stage == states.VocabCreation.waiting_for_vocab_name:
        kb: InlineKeyboardMarkup = get_kb_create_vocab_name()
        msg_text: str = add_vocab_data_to_message(vocab_name, vocab_description, MSG_ENTER_VOCAB_NAME)

    elif previous_stage == states.VocabCreation.waiting_for_vocab_description:
        kb: InlineKeyboardMarkup = get_kb_create_vocab_description()
        msg_text: str = add_vocab_data_to_message(vocab_name, vocab_description, MSG_ENTER_VOCAB_DESCRIPTION)

    elif previous_stage == states.VocabCreation.waiting_for_wordpairs:
        kb: InlineKeyboardMarkup = get_kb_create_wordpairs()
        msg_text: str = add_vocab_data_to_message(vocab_name, vocab_description, MSG_ENTER_WORDPAIRS)

    await callback.message.edit_text(text=msg_text, reply_markup=kb)
