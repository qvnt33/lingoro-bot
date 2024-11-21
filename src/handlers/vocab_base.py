import logging
from typing import Any

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from db.crud import VocabCRUD, WordpairCRUD
from db.database import Session
from exceptions import InvalidVocabIndexError
from src.filters.check_empty_filters import CheckEmptyFilter
from src.keyboards.vocab_base_kb import (
    get_inline_kb_accept_delete_vocab,
    get_inline_kb_confirm_delete,
    get_inline_kb_vocab_options,
    get_inline_kb_vocab_selection_base,
)
from text_data import (
    MSG_CHOOSE_VOCAB,
    MSG_CONFIRM_DELETE_VOCAB,
    MSG_ERROR_VOCAB_BASE_EMPTY,
    MSG_INFO_VOCAB,
    MSG_SUCCESS_VOCAB_DELETED,
    TEMPLATE_WORDPAIR,
)
from tools.wordpair_utils import format_word_items

router = Router(name='vocab_base')
logger: logging.Logger = logging.getLogger(__name__)


@router.callback_query(F.data == 'vocab_base')
async def process_vocab_base(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "База словників" у головному меню.
    Відправляє користувачу користувацькі словники у вигляді кнопок.
    """
    user_id: int = callback.from_user.id

    logger.info(f'Користувач перейшов до розділу "База словників". USER_ID: {user_id}')

    check_empty_filter = CheckEmptyFilter()

    await state.clear()
    logger.info('FSM стан та FSM-Cache очищено')

    with Session() as session:
        vocab_crud = VocabCRUD(session)

        # Дані всіх користувацьких словників користувача
        all_vocabs_data: list[dict] = vocab_crud.get_all_vocabs_data(user_id)

    # Якщо в БД користувача немає користувацьких словників
    if check_empty_filter.apply(all_vocabs_data):
        logger.info('В БД користувача немає користувацьких словників')
        msg_text: str = MSG_ERROR_VOCAB_BASE_EMPTY
    else:
        msg_text: str = MSG_CHOOSE_VOCAB

    kb: InlineKeyboardMarkup = get_inline_kb_vocab_selection_base(all_vocabs_data)
    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.callback_query(F.data.startswith('select_vocab_base'))
async def process_vocab_base_selection(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку користувацького словника у розділі "База словників".
    Відправляє користувачу його статистику з словниковими парами та клавіатуру для взаємодії з ним.
    """
    vocab_id = int(callback.data.split('_')[-1])
    logger.info(f'Був обраний користувацький словник у розділі "База словників". VOCAB_ID: {vocab_id}')

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

    kb: InlineKeyboardMarkup = get_inline_kb_vocab_options()

    formatted_wordpairs: list[str] = []

    for idx, wordpair_item in enumerate(sorted_wordpair_items, start=1):
        word_items: list[dict] = wordpair_item.get('words')
        translation_items: list[dict] = wordpair_item.get('translations')
        annotation: str = wordpair_item.get('annotation') or 'Немає анотації'
        wordpair_number_errors: int = wordpair_item.get('number_errors')

        formatted_word_items: list[str] = format_word_items(word_items)
        formatted_translation_items: list[str] = format_word_items(translation_items, is_translation_items=True)

        formatted_wordpair: str = TEMPLATE_WORDPAIR.format(idx=idx,
                                                           words=formatted_word_items,
                                                           translations=formatted_translation_items,
                                                           annotation=annotation,
                                                           number_errors=wordpair_number_errors)
        formatted_wordpairs.append(formatted_wordpair)

    joined_wordpairs: str = '\n'.join(formatted_wordpairs)

    msg_vocab_info: str = MSG_INFO_VOCAB.format(name=vocab_name,
                                                description=vocab_description,
                                                wordpairs_count=vocab_wordpairs_count,
                                                number_errors=vocab_number_errors,
                                                wordpairs=joined_wordpairs)

    await callback.message.edit_text(text=msg_vocab_info, reply_markup=kb)


@router.callback_query(F.data == 'delete_vocab')
async def process_delete_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Видалити словник" після обрання користувацького словника
    у розділі "База словників".
    Відправляє клавіатуру для підтвердження видалення.
    """
    logger.info('Натиснуто кнопку "Видалити словник"')

    data_fsm: dict[str, Any] = await state.get_data()
    vocab_id: int | None = data_fsm.get('vocab_id')

    try:
        with Session() as session:
            vocab_crud = VocabCRUD(session)
            vocab_data: dict[str, Any] = vocab_crud.get_vocab_data(vocab_id)
            vocab_name: str = vocab_data.get('name')
    except InvalidVocabIndexError as e:
        logger.error(e)
        return

    kb: InlineKeyboardMarkup = get_inline_kb_confirm_delete()
    msg_confirm_delete_vocab: str = MSG_CONFIRM_DELETE_VOCAB.format(name=vocab_name)

    await callback.message.edit_text(text=msg_confirm_delete_vocab, reply_markup=kb)


@router.callback_query(F.data == 'accept_delete_vocab')
async def process_accept_delete_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Так" при підтвердженні видалення користувацького словника.
    Мʼяко видаляє користувацький словник, залишаючи всі його звʼязки в БД.
    """
    logger.info('Натиснуто кнопку "Так" під час підтвердження видалення словника')

    data_fsm: dict[str, Any] = await state.get_data()
    vocab_id: int | None = data_fsm.get('vocab_id')

    try:
        with Session() as session:
            vocab_crud = VocabCRUD(session)

            vocab_data: dict[str, Any] = vocab_crud.get_vocab_data(vocab_id)
            vocab_name: str | None = vocab_data.get('name')

            vocab_crud.soft_delete_vocab(vocab_id)

            logger.info('Словник був видалений з БД')
    except InvalidVocabIndexError as e:
        logger.error(e)
        return

    kb: InlineKeyboardMarkup = get_inline_kb_accept_delete_vocab()
    msg_vocab_deleted: str = MSG_SUCCESS_VOCAB_DELETED.format(name=vocab_name)

    await callback.message.edit_text(text=msg_vocab_deleted, reply_markup=kb)
