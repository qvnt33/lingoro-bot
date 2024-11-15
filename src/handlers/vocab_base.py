import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from db.crud import VocabCRUD
from db.database import Session
from exceptions import InvalidVocabIndexError
from src.filters.check_empty_filters import CheckEmptyFilter
from src.keyboards.vocab_base_kb import get_inline_kb_vocab_base
from src.keyboards.vocab_selection_kb import get_inline_kb_vocab_selection
from text_data import MSG_CHOOSE_VOCAB, MSG_ERROR_VOCAB_BASE_EMPTY

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

        # Дані всіх словників користувача
        all_vocabs_data: list[dict] = vocab_crud.get_data_all_vocabs(user_id)

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

            wordpair_items: list[dict] = vocab_crud.get_wordpairs_by_vocab_id(vocab_id)
            vocab_data: dict = vocab_crud.get_vocab_data_by_id(vocab_id)
    except InvalidVocabIndexError as e:
        logger.error(e)
        return

    vocab_name: str = vocab_data['name']
    vocab_description: str = vocab_data['description'] or 'Відсутній'
    vocab_number_errors: int = vocab_data['number_errors']
    vocab_wordpairs_count: int = vocab_data['wordpairs_count']

    kb: InlineKeyboardMarkup = get_inline_kb_vocab_base()

    formatted_wordpairs: list[str] = []

    for idx, wordpair_item in enumerate(iterable=wordpair_items, start=1):
        word_items: list[dict] = wordpair_item['words']
        translation_items: list[dict] = wordpair_item['translations']
        annotation: str = wordpair_item['annotation'] or 'Немає анотації'
        wordpair_number_errors: int = wordpair_item['number_errors']

        formatted_word_items: list[str] = format_word_items(word_items)
        formatted_translation_items: list[str] = format_translation_items(translation_items)

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


def format_word_items(word_items: list[dict]) -> list[str]:
    formatted_words: list[str] = []

    for word_item in word_items:
        word: str = word_item['word']
        transcription: str | None = word_item['transcription']

        formatted_word: str = (f'{word} [{transcription}]' if transcription is not None
                                else word)
        formatted_words.append(formatted_word)

    joined_words: str = ', '.join(formatted_words)
    return joined_words


def format_translation_items(translation_items: list[dict]) -> list[str]:
    formatted_translations: list[str] = []

    for translation_item in translation_items:
        translation: str = translation_item['translation']
        transcription: str | None = translation_item['transcription']

        formatted_translation: str = (f'{translation} [{transcription}]' if transcription is not None
                                        else translation)
        formatted_translations.append(formatted_translation)

    joined_translations: str = ', '.join(formatted_translations)
    return joined_translations








'''
@router.callback_query(F.data.startswith('select_vocab_training'))
async def process_training_vocab_selection(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обробка вибору словника для тренування."""
    data_fsm: dict[str, Any] = await state.get_data()
    vocab_id = int(callback.data.split('_')[-1])

    await state.update_data(vocab_id=vocab_id)  # Додавання ID обраного словника

    with Session() as db:
        vocab_details: list[dict] = get_wordpairs_by_vocab_id(db, vocab_id)
        user_vocab: dict = get_user_vocab_by_vocab_id(db, vocab_id)

    vocab_name: str = user_vocab.name
    vocab_note: str = user_vocab.description

    current_state: Any | None = data_fsm.get('current_state')  # Поточний стан FSM

    # Якщо був викликаний список словників з розділу бази словників
    if current_state == 'VocabBaseState':
        kb: InlineKeyboardMarkup = get_inline_kb_vocab_options()
        msg_finally: str = (
            f'Назва словника: {vocab_name}\n'
            f'Примітка: {vocab_note or 'Відсутня'}\n'
            f'Кількість словникових пар: {len(vocab_details)}\n\n'
            f'Словникові пари:\n')

        for idx, wordpairs_data in enumerate(vocab_details, start=1):
            words_lst: list[tuple[str, str]] = wordpairs_data['words']
            translations_lst: list[tuple[str, str]] = wordpairs_data['translations']
            annotation: str = wordpairs_data['annotation'] or 'Немає анотації'

            words_part: str = ', '.join([f'{word} [{transcription}]'
                                    if transcription else word
                                    for word, transcription in words_lst])
            translations_part: str = ', '.join([f'{translation} [{transcription}]'
                                        if transcription else translation
                                        for translation, transcription in translations_lst])

            msg_finally += f'{idx}. {words_part} : {translations_part} : {annotation}\n'
    # Якщо був викликаний список словників з розділу тренування
    elif current_state == 'VocabTrainState':
        msg_finally: str = f'Ви обрали словник: {vocab_name}\nОберіть, будь-ласка, тип тренування.'
        kb: InlineKeyboardMarkup = get_inline_kb_all_training()

    await callback.message.edit_text(text=msg_finally, reply_markup=kb)
'''
