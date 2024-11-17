import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from db.crud import VocabCRUD, WordpairCRUD
from db.database import Session
from exceptions import InvalidVocabIndexError
from src.filters.check_empty_filters import CheckEmptyFilter
from src.keyboards.vocab_base_kb import get_inline_kb_vocab_base
from src.keyboards.vocab_selection_kb import get_inline_kb_vocab_selection
from text_data import MSG_CHOOSE_VOCAB, MSG_ERROR_VOCAB_BASE_EMPTY
from tools.wordpair_utils import format_word_items

router = Router(name='vocab_base')
logger: logging.Logger = logging.getLogger(__name__)


@router.callback_query(F.data == 'vocab_base')
async def process_vocab_base(callback: types.CallbackQuery) -> None:
    """Відстежує натискання на кнопку "База словників" у головному меню.
    Відправляє користувачу словники у вигляді кнопок.
    """
    user_id: int = callback.from_user.id
    check_empty_filter = CheckEmptyFilter()

    with Session() as session:
        vocab_crud = VocabCRUD(session)

        # Дані всіх користувацьких словників користувача
        all_vocabs_data: list[dict] = vocab_crud.get_all_vocabs_data(user_id)

    # Якщо в БД користувача немає словників
    if check_empty_filter.apply(all_vocabs_data):
        msg_text: str = MSG_ERROR_VOCAB_BASE_EMPTY
    else:
        msg_text: str = MSG_CHOOSE_VOCAB

    kb: InlineKeyboardMarkup = get_inline_kb_vocab_selection(all_vocabs_data=all_vocabs_data,
                                                             callback_prefix='select_vocab_base')

    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.callback_query(F.data.startswith('select_vocab_base'))
async def process_vocab_base_selection(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обробка вибору словника у базі словників"""
    vocab_id = int(callback.data.split('_')[-1])

    await state.update_data(vocab_id=vocab_id)
    logger.info('ID словника збережений у FSM-Cache')

    try:
        with Session() as session:
            vocab_crud = VocabCRUD(session)
            wordpair_crud = WordpairCRUD(session)

            wordpair_items: list[dict] = wordpair_crud.get_wordpairs(vocab_id)

            # Відсортований список словникових пар по кількості їх помилок
            sorted_wordpair_items: list[dict] = sorted(wordpair_items,
                                                       key=lambda item: item['number_errors'],
                                                       reverse=True)
            vocab_data: dict = vocab_crud.get_vocab_data(vocab_id)
    except InvalidVocabIndexError as e:
        logger.error(e)
        return

    vocab_name: str = vocab_data['name']
    vocab_description: str = vocab_data['description'] or 'Відсутній'
    vocab_number_errors: int = vocab_data['number_errors']
    vocab_wordpairs_count: int = vocab_data['wordpairs_count']

    kb: InlineKeyboardMarkup = get_inline_kb_vocab_base()

    formatted_wordpairs: list[str] = []

    for idx, wordpair_item in enumerate(iterable=sorted_wordpair_items, start=1):
        word_items: list[dict] = wordpair_item['words']
        translation_items: list[dict] = wordpair_item['translations']
        annotation: str = wordpair_item['annotation'] or 'Немає анотації'
        wordpair_number_errors: int = wordpair_item['number_errors']

        formatted_word_items: list[str] = format_word_items(word_items)
        formatted_translation_items: list[str] = format_word_items(translation_items, is_translation_items=True)

        formatted_wordpair: str = (
            f'{idx}. {formatted_word_items} ▪️ '
            f'{formatted_translation_items} ▪️ '
            f'{annotation}\n'
            f'🔺 Помилки: {wordpair_number_errors}\n')
        formatted_wordpairs.append(formatted_wordpair)

    joined_wordpairs: str = '\n'.join(formatted_wordpairs)

    msg_text: str = (
        f'📚 Назва словника: {vocab_name}\n'
        f'📄 Опис: {vocab_description}\n'
        f'🔢 Кількість словникових пар: {vocab_wordpairs_count}\n'
        f'⚠️ Загальна кількість помилок: {vocab_number_errors}\n\n'
        f'Словникові пари:\n'
        f'{joined_wordpairs}')

    await callback.message.edit_text(text=msg_text, reply_markup=kb)
