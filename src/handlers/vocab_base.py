import logging
from typing import Any

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from db.crud import VocabCRUD, WordpairCRUD
from db.database import Session
from exceptions import InvalidVocabIndexError
from src.filters.check_empty_filters import CheckEmptyFilter
from src.keyboards.vocab_base_kb import (
    get_kb_confirm_delete,
    get_kb_vocab_options,
    get_kb_vocab_selection_base,
)
from text_data import (
    MSG_CHOOSE_VOCAB,
    MSG_CONFIRM_DELETE_VOCAB,
    MSG_INFO_VOCAB_BASE_EMPTY,
    MSG_SUCCESS_VOCAB_DELETED,
)
from tools.vocab_utils import format_vocab_info
from tools.wordpair_utils import get_formatted_wordpairs_list

router = Router(name='vocab_base')
logger: logging.Logger = logging.getLogger(__name__)


@router.callback_query(F.data == 'vocab_base')
async def process_vocab_base(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "База словників" у головному меню.
    Відправляє користувачу користувацькі словники у вигляді кнопок.
    """
    user_id: int = callback.from_user.id

    logger.info(f'Користувач перейшов до розділу "База словників". USER_ID: {user_id}')

    await state.clear()
    logger.info('FSM стан та FSM-Cache очищено перед запуском розділу "База словників"')

    with Session() as session:
        vocab_crud = VocabCRUD(session)

        # Дані всіх користувацьких словників користувача
        all_vocabs_data: list[dict] = vocab_crud.get_all_vocabs_data(user_id)

    # Якщо в БД користувача немає користувацьких словників
    check_empty_filter = CheckEmptyFilter()
    if check_empty_filter.apply(all_vocabs_data):
        logger.info('В БД користувача немає користувацьких словників')
        msg_text: str = MSG_INFO_VOCAB_BASE_EMPTY
    else:
        msg_text: str = MSG_CHOOSE_VOCAB

    kb: InlineKeyboardMarkup = get_kb_vocab_selection_base(all_vocabs_data[::-1])
    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.message(Command(commands=['vocab_base']))
async def cmd_vocab_base(message: types.Message, state: FSMContext) -> None:
    """Відстежує введення команди "vocab_base".
    Відправляє користувачу користувацькі словники у вигляді кнопок.
    """
    user_id: int = message.from_user.id

    logger.info(f'Користувач ввів команду "{message.text}"')
    logger.info(f'Користувач перейшов до розділу "База словників". USER_ID: {user_id}')

    await state.clear()
    logger.info('FSM стан та FSM-Cache очищено перед запуском розділу "База словників"')

    with Session() as session:
        vocab_crud = VocabCRUD(session)

        # Дані всіх користувацьких словників користувача
        all_vocabs_data: list[dict] = vocab_crud.get_all_vocabs_data(user_id)

    # Якщо в БД користувача немає користувацьких словників
    check_empty_filter = CheckEmptyFilter()
    if check_empty_filter.apply(all_vocabs_data):
        logger.info('В БД користувача немає користувацьких словників')
        msg_text: str = MSG_INFO_VOCAB_BASE_EMPTY
    else:
        msg_text: str = MSG_CHOOSE_VOCAB

    kb: InlineKeyboardMarkup = get_kb_vocab_selection_base(all_vocabs_data[::-1])
    await message.answer(text=msg_text, reply_markup=kb)


@router.callback_query(F.data.startswith('select_vocab_base'))
async def process_vocab_base_selection(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку користувацького словника у розділі "База словників".
    Відправляє користувачу його статистику з словниковими парами та клавіатуру для взаємодії з ним.
    """
    vocab_id = int(callback.data.split('_')[-1])
    logger.info(f'Обрано користувацький словник у розділі "База словників". VOCAB_ID: {vocab_id}')

    await state.update_data(vocab_id=vocab_id)
    logger.info('ID користувацького словника збережений у FSM-Cache')

    try:
        with Session() as session:
            vocab_crud = VocabCRUD(session)
            wordpair_crud = WordpairCRUD(session)

            wordpair_items: list[dict] = wordpair_crud.get_wordpairs(vocab_id)

            # Відсортований список словникових пар по кількості їх помилок
            sorted_wordpair_items: list[dict] = sorted(wordpair_items,
                                                       key=lambda item: item['number_errors'],
                                                       reverse=True)
            vocab_data: dict[str, Any] = vocab_crud.get_vocab_data(vocab_id)
    except InvalidVocabIndexError as e:
        logger.error(e)
        return

    vocab_name: str = vocab_data.get('name')
    vocab_description: str = vocab_data.get('description') or 'Відсутній'
    vocab_number_errors: int = vocab_data.get('number_errors')
    vocab_wordpairs_count: int = vocab_data.get('wordpairs_count')

    kb: InlineKeyboardMarkup = get_kb_vocab_options()
    formatted_wordpairs: list[str] = get_formatted_wordpairs_list(sorted_wordpair_items)

    msg_vocab_info: str = format_vocab_info(name=vocab_name,
                                            description=vocab_description,
                                            wordpairs_count=vocab_wordpairs_count,
                                            number_errors=vocab_number_errors,
                                            wordpairs=formatted_wordpairs)
    await callback.message.edit_text(text=msg_vocab_info, reply_markup=kb)


@router.callback_query(F.data == 'delete_vocab')
async def process_delete_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Видалити словник" після обрання користувацького словника
    у розділі "База словників".
    Відправляє клавіатуру для підтвердження видалення.
    """
    logger.info('Обрано видалення користувацького словника')

    data_fsm: dict[str, Any] = await state.get_data()
    vocab_id: int | None = data_fsm.get('vocab_id')

    try:
        with Session() as session:
            vocab_crud = VocabCRUD(session)
            vocab_data: dict[str, Any] = vocab_crud.get_vocab_data(vocab_id)
    except InvalidVocabIndexError as e:
        logger.error(e)
        return

    kb: InlineKeyboardMarkup = get_kb_confirm_delete()

    vocab_name: str = vocab_data.get('name')
    msg_confirm_delete_vocab: str = MSG_CONFIRM_DELETE_VOCAB.format(name=vocab_name)

    await callback.message.edit_text(text=msg_confirm_delete_vocab, reply_markup=kb)


@router.callback_query(F.data == 'accept_delete_vocab')
async def process_accept_delete_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Так" при підтвердженні видалення користувацького словника.
    Мʼяко видаляє користувацький словник, позначаючи його як 'видалений' (.is_deleted=True).
    Відправляє користувачу користувацькі словники у вигляді кнопок.
    """
    logger.info('Підтверджено видалення користувацького словника')

    data_fsm: dict[str, Any] = await state.get_data()
    vocab_id: int = data_fsm.get('vocab_id')

    user_id: int = callback.from_user.id

    try:
        with Session() as session:
            vocab_crud = VocabCRUD(session)
            vocab_data: dict[str, Any] = vocab_crud.get_vocab_data(vocab_id)

            vocab_crud.soft_delete_vocab(vocab_id)
            logger.info('Користувацький словник був "мʼяко" видалений з БД')

            # Дані всіх користувацьких словників користувача
            all_vocabs_data: list[dict] = vocab_crud.get_all_vocabs_data(user_id)
    except InvalidVocabIndexError as e:
        logger.error(e)
        return

    vocab_name: str = vocab_data.get('name')

    # Якщо в БД користувача немає користувацьких словників
    check_empty_filter = CheckEmptyFilter()
    if check_empty_filter.apply(all_vocabs_data):
        logger.info('В БД користувача немає користувацьких словників')
        msg_text: str = '\n\n'.join((MSG_SUCCESS_VOCAB_DELETED.format(name=vocab_name),
                                     MSG_INFO_VOCAB_BASE_EMPTY))
    else:
        msg_text: str = '\n\n'.join((MSG_SUCCESS_VOCAB_DELETED.format(name=vocab_name),
                                     MSG_CHOOSE_VOCAB))

    kb: InlineKeyboardMarkup = get_kb_vocab_selection_base(all_vocabs_data[::-1])

    await callback.message.edit_text(text=msg_text, reply_markup=kb)
