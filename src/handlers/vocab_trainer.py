import logging
import random
from typing import Any, Dict, List

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from db.crud import VocabCRUD, WordpairCRUD
from db.database import Session
from db.models import User
from exceptions import InvalidVocabIndexError
from src.filters.check_empty_filters import CheckEmptyFilter
from src.fsm.states import VocabTraining
from src.keyboards.vocab_base_kb import get_inline_kb_vocab_base
from src.keyboards.vocab_selection_kb import get_inline_kb_vocab_selection
from src.keyboards.vocab_trainer_kb import get_inline_kb_all_training, get_inline_kb_process_training, get_inline_kb_vocab_selection_training
from text_data import (
    MSG_CHOOSE_TRAINING_TYPE,
    MSG_CHOOSE_VOCAB_FOR_TRAINING,
    MSG_ERROR_VOCAB_BASE_EMPTY,
    MSG_ERROR_VOCAB_BASE_EMPTY_FOR_TRAINING,
    MSG_INFO_VOCAB,
    TEMPLATE_WORDPAIR,
)
from tools.wordpair_utils import format_word_items

router = Router(name='vocab_trainer')
logger: logging.Logger = logging.getLogger(__name__)


@router.callback_query(F.data == 'vocab_trainer')
async def process_vocab_base(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Тренування" у головному меню.
    Відправляє користувачу користувацькі словники у вигляді кнопок.
    """
    user_id: int = callback.from_user.id

    logger.info(f'Користувач перейшов до розділу "Тренування". USER_ID: {user_id}')

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
        msg_text: str = MSG_ERROR_VOCAB_BASE_EMPTY_FOR_TRAINING
        kb: InlineKeyboardMarkup = get_inline_kb_vocab_selection_training(all_vocabs_data,
                                                             callback_prefix='select_vocab_training',
                                                             is_with_btn_vocab_base=True)
    else:
        msg_text: str = MSG_CHOOSE_VOCAB_FOR_TRAINING

        kb: InlineKeyboardMarkup = get_inline_kb_vocab_selection_training(all_vocabs_data,
                                                                callback_prefix='select_vocab_training')
    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.callback_query(F.data.startswith('select_vocab_training'))
async def process_training_selection(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку користувацького словника у розділі "Тренування".
    Відправляє клавіатуру з вибором типу тренування.
    """
    vocab_id = int(callback.data.split('_')[-1])
    logger.info(f'Був обраний користувацький словник у розділі "Тренування". VOCAB_ID: {vocab_id}')

    await state.update_data(vocab_id=vocab_id)
    logger.info('ID користувацького словника збережений у FSM-Cache')

    try:
        with Session() as session:
            vocab_crud = VocabCRUD(session)
            vocab_data: dict[str, Any] = vocab_crud.get_vocab_data(vocab_id)

            wordpair_crud = WordpairCRUD(session)
            wordpair_items: list[dict] = wordpair_crud.get_wordpairs(vocab_id)
    except InvalidVocabIndexError as e:
        logger.error(e)
        return

    kb: InlineKeyboardMarkup = get_inline_kb_all_training()
    vocab_name: str = vocab_data.get('name')
    msg_choose_training_type: str = MSG_CHOOSE_TRAINING_TYPE.format(name=vocab_name)

    wordpairs_count: int = vocab_data.get('wordpairs_count')

    # Список індексів, які ще не були використані
    available_idxs = list(range(wordpairs_count))

    await state.update_data(vocab_data=vocab_data,
                            wordpair_items=wordpair_items,
                            available_idxs=available_idxs)

    await callback.message.edit_text(text=msg_choose_training_type, reply_markup=kb)


@router.callback_query(F.data == 'direct_translation')
async def process_btn_direct_translation(callback: CallbackQuery, state: FSMContext) -> None:
    """Ініціалізація тренування і збереження даних у FSM"""
    await state.update_data(current_training_type='direct_translation')

    # Надсилаємо першу пару на переклад
    await send_next_word(callback.message, state)


@router.callback_query(F.data == 'reverse_translation')
async def process_btn_reverse_translation(callback: CallbackQuery, state: FSMContext) -> None:
    """Ініціалізація тренування і збереження даних у FSM"""
    data_fsm: Dict[str, Any] = await state.get_data()
    vocab_id: int = data_fsm.get('vocab_id')

    with Session() as db:
        vocab_details: List[Dict] = get_wordpairs_by_vocab_id(db, vocab_id)

    # Список індексів, які ще не були використані
    available_idxs = list(range(len(vocab_details)))

    # Збереження всіх деталей у стані FSM
    await state.update_data(vocab_details=vocab_details, available_idxs=available_idxs, current_training_type='reverse_translation')

    # Надсилаємо першу пару на переклад
    await send_next_word(callback.message, state)


async def send_next_word(message: Message, state: FSMContext) -> None:
    """Надсилає наступне слово для перекладу"""
    data_fsm: dict[str, Any] = await state.get_data()

    vocab_data: dict[str, Any] = data_fsm.get('vocab_data')
    wordpair_items: list[dict] = data_fsm.get('wordpair_items')

    available_idxs: list = data_fsm.get('available_idxs', [])  # Список індексів, які ще не були використані
    preview_wordpair_idx: int = data_fsm.get('wordpair_idx', 0)  # Минулий індекс
    current_training_type: str = data_fsm.get('current_training_type')  # Тип тренування
    wordpair_idx = 0

    # Вибір випадкового індексу з тих, що ще не були використані
    if len(available_idxs) == 1:
        wordpair_idx: int = available_idxs[0]
    elif len(available_idxs) > 1:
        # Оновлення індексу (щоб не збігався з минулим)
        while wordpair_idx == preview_wordpair_idx:
            wordpair_idx: int = random.choice(available_idxs)  # Індекс словникової пари
        await state.update_data(wordpair_idx=wordpair_idx)
    else:
        kb: InlineKeyboardMarkup = get_inline_kb_all_training()
        await message.answer(text='Всі словникові пари переведені. Тренування завершено!', reply_markup=kb)
        vocab_id: int = data_fsm.get('vocab_id')
        await state.clear()  # Очищення FSM-кеш та FSM-стану
        await state.update_data(vocab_id=vocab_id)  # Оновлення індексу
        return

    wordpair_data: dict = wordpair_items[wordpair_idx]
    wordpair_words = wordpair_data.get('words')
    wordpair_translations = wordpair_data.get('translations')
    wordpair_annotation = wordpair_data.get('annotation')
    wordpair_number_errors = wordpair_data.get('number_errors')

    if current_training_type == 'direct_translation':
        formatted_word = ', '.join(f'{word_item.get("word")} [{word_item.get("transcription")}]'
                                   if word_item.get('transcription') else word_item.get('word')
                                   for word_item in wordpair_words)
        formatted_translation = ', '.join(f'{translation_item.get("translation")} [{translation_item.get("transcription")}]'
                                          if translation_item.get('transcription') else translation_item.get('translation')
                                          for translation_item in wordpair_translations)
        correct_translations = [translation.get('translation').lower() for translation in wordpair_translations]
    elif current_training_type == 'reverse_translation':
        formatted_translation = ', '.join(f'{word_item.get("word")} [{word_item.get("transcription")}]'
                                          if word_item.get('transcription') else word_item.get('word')
                                          for word_item in wordpair_words)
        formatted_word = ', '.join(f'{translation_item.get("translation")} [{translation_item.get("transcription")}]'
                                   if translation_item.get('transcription') else translation_item.get('translation')
                                   for translation_item in wordpair_translations)
        correct_translations = [translation.get('word').lower() for translation in wordpair_words]

    await state.update_data(formatted_word=formatted_word,
                            formatted_translation=formatted_translation,
                            wordpair_idx=wordpair_idx,
                            correct_translations=correct_translations)
    kb: InlineKeyboardMarkup = get_inline_kb_process_training()  # Клавіатура для тренування

    await message.answer(text=f'Перекладіть слово: {formatted_word}', reply_markup=kb)

    # Оновлюємо стан на очікування відповіді
    await state.set_state(VocabTraining.waiting_for_translation)


@router.message(VocabTraining.waiting_for_translation)
async def process_translation(message: Message, state: FSMContext) -> None:
    """Обробляє переклад, введений користувачем"""
    data_fsm: Dict[str, Any] = await state.get_data()

    wordpair_idx = data_fsm.get('wordpair_idx')

    formatted_word = data_fsm.get('formatted_word')
    formatted_translation = data_fsm.get('formatted_translation')

    available_idxs = data_fsm.get('available_idxs', [])  # Список індексів, які ще не були використані
    correct_translations = data_fsm.get('correct_translations')

    # Переклади без анотацій
    print(correct_translations)
    user_translation: str = message.text.strip().lower()  # Введений користувачем переклад
    print(user_translation)
    if user_translation in correct_translations:
        await message.answer(f'Правильно!\n{formatted_word} -> {formatted_translation}')
        available_idxs.remove(wordpair_idx)
        await state.update_data(available_idxs=available_idxs)  # Оновлення індексу
        await send_next_word(message, state)
    else:
        await message.answer('Не Правильно!')
        await send_next_word(message, state)


@router.callback_query(F.data == 'cancel_training')
async def process_cancel_training(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Скасувати" під час тренування"""
    data_fsm: Dict[str, Any] = await state.get_data()
    # vocab_id: int = data_fsm.get('vocab_id')
    await state.clear()  # Очищення FSM-кеш та FSM-стану
    # await state.update_data(vocab_id=vocab_id)  # Оновлення індексу
    kb: InlineKeyboardMarkup = get_inline_kb_all_training()
    vocab_name: str = 'vocab_data.get(name)'
    msg_choose_training_type: str = MSG_CHOOSE_TRAINING_TYPE.format(name=vocab_name)
    await callback.message.edit_text(text=msg_choose_training_type, reply_markup=kb)



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
