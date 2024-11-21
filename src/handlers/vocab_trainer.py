import logging
import random
from datetime import datetime
from typing import Any, Dict, List

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup

from db.crud import TrainingCRUD, VocabCRUD, WordpairCRUD
from db.database import Session
from exceptions import InvalidVocabIndexError
from src.filters.check_empty_filters import CheckEmptyFilter
from src.fsm.states import VocabTraining
from src.keyboards.vocab_trainer_kb import (
    get_kb_all_training,
    get_kb_confirm_cancel_training,
    get_kb_finish_training,
    get_kb_process_training,
    get_kb_vocab_selection_training,
)
from text_data import (
    MSG_CHOOSE_TRAINING_MODE,
    MSG_CHOOSE_VOCAB_FOR_TRAINING,
    MSG_CONFIRM_CANCEL_TRAINING,
    MSG_INFO_VOCAB_BASE_EMPTY_FOR_TRAINING,
)
from tools.training_utils import format_training_message
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
        msg_text: str = MSG_INFO_VOCAB_BASE_EMPTY_FOR_TRAINING
        kb: InlineKeyboardMarkup = get_kb_vocab_selection_training(all_vocabs_data, is_with_btn_vocab_base=True)
    else:
        msg_text: str = MSG_CHOOSE_VOCAB_FOR_TRAINING
        kb: InlineKeyboardMarkup = get_kb_vocab_selection_training(all_vocabs_data)
    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.callback_query(F.data.startswith('select_vocab_training'))
async def process_training_selection(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку користувацького словника у розділі "Тренування".
    Відправляє клавіатуру з вибором типу тренування.
    """
    vocab_id = int(callback.data.split('_')[-1])
    logger.info(f'Був обраний користувацький словник у розділі "Тренування". VOCAB_ID: {vocab_id}')

    try:
        with Session() as session:
            vocab_crud = VocabCRUD(session)
            vocab_data: dict[str, Any] = vocab_crud.get_vocab_data(vocab_id)

            wordpair_crud = WordpairCRUD(session)
            wordpair_items: list[dict] = wordpair_crud.get_wordpairs(vocab_id)
    except InvalidVocabIndexError as e:
        logger.error(e)
        return

    kb: InlineKeyboardMarkup = get_kb_all_training()
    vocab_name: str = vocab_data.get('name')
    msg_choose_training_mode: str = MSG_CHOOSE_TRAINING_MODE.format(name=vocab_name)

    wordpairs_count: int = vocab_data.get('wordpairs_count')

    await state.update_data(vocab_id=vocab_id,
                            vocab_data=vocab_data,
                            wordpair_items=wordpair_items,
                            wordpairs_count=wordpairs_count)
    logger.info('ID користувацького словника збережений у FSM-Cache')

    await callback.message.edit_text(text=msg_choose_training_mode, reply_markup=kb)


@router.callback_query(F.data == 'direct_translation')
async def process_btn_direct_translation(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Ініціалізація тренування та збереження даних у FSM"""
    await callback.message.delete()

    data_fsm: dict[str, Any] = await state.get_data()
    wordpairs_count: int = data_fsm.get('wordpairs_count')
    start_time_training: datetime = datetime.now()
    await state.update_data(start_time_training=start_time_training)
    # Список індексів, які ще не були використані
    available_idxs = list(range(wordpairs_count))

    await state.update_data(current_training_mode='direct_translation',
                            available_idxs=available_idxs)
    await send_next_word(callback.message, state)


@router.callback_query(F.data == 'reverse_translation')
async def process_btn_reverse_translation(callback: types.CallbackQuery, state: FSMContext) -> None:
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


def get_random_wordpair_idx(available_idxs: list, preview_idx: int) -> int:
    """Повертає випадковий індекс словникової пари із доступних.
    Якщо кількість доступних індексів більша за один, то обраний новий індекс не повинен збігатися з попереднім.

    Args:
        available_idxs (list): Список доступних індексів.
        preview_idx (int): Попередній індекс.

    Returns:
        int: Випадковий індекс.
    """
    if len(available_idxs) == 1:
        return available_idxs[0]

    # Якщо індексів більше одного, то обирається новий індекс
    wordpair_idx: int = random.choice(available_idxs)
    while wordpair_idx == preview_idx:
        wordpair_idx: int = random.choice(available_idxs)

    return wordpair_idx


async def send_next_word(message: types.Message, state: FSMContext) -> None:
    """Відправляє наступне слово для перекладу"""
    data_fsm: dict[str, Any] = await state.get_data()

    # Прапор для перевірки: використовувати поточне слово чи обрати нове
    use_current_word: bool = data_fsm.get('use_current_word', False)

    vocab_data: dict[str, Any] = data_fsm.get('vocab_data')
    wordpair_items: list[dict] = data_fsm.get('wordpair_items')

    vocab_name: str = vocab_data.get('name')
    available_idxs: list = data_fsm.get('available_idxs', [])  # Список індексів, які ще не були використані

    current_training_mode: str = data_fsm.get('current_training_mode')  # Тип тренування

    training_number_errors: int = data_fsm.get('training_number_errors', 0)  # Кількість помилок за тренування
    current_training_count: int = data_fsm.get('current_training_count', 1)  # Кількість тренувань поспіль

    check_empty_filter = CheckEmptyFilter()

    # Якщо не залишилось невикористаних індексів
    if check_empty_filter.apply(available_idxs):
        kb: InlineKeyboardMarkup = get_kb_finish_training()

        msg_choose_training_mode: str = MSG_CHOOSE_TRAINING_MODE.format(name=vocab_name)
        msg_text: str = f'Всі словникові пари переведені. Тренування завершено!\n\n{msg_choose_training_mode}'
        await state.update_data(training_number_errors=0,
                                training_is_completed=True)

        await finish_training(message, state)
        await message.answer(text=msg_text, reply_markup=kb)
        return

    preview_wordpair_idx: int = data_fsm.get('wordpair_idx', 0)  # Минулий індекс

    if use_current_word:
        wordpair_idx: int = preview_wordpair_idx
        await state.update_data(use_current_word=False)
    else:
        # Вибір випадкового індексу з тих, що ще не були використані
        wordpair_idx: int = get_random_wordpair_idx(available_idxs, preview_wordpair_idx)
    await state.update_data(wordpair_idx=wordpair_idx)

    wordpair_item: dict[str, Any] = wordpair_items[wordpair_idx]

    # Список всіх слів та перекладів словникової пари з їх транскрипціями
    word_items: list[dict] = wordpair_item.get('words')
    translation_items: list[dict] = wordpair_item.get('translations')
    wordpair_annotation = wordpair_item.get('annotation') or 'Відсутня'

    if current_training_mode == 'direct_translation':
        formatted_words: str = format_word_items(word_items)
        formatted_translations: str = format_word_items(translation_items, is_translation_items=True)
        correct_translations: list = [translation.get('translation').lower() for translation in translation_items]
    elif current_training_mode == 'reverse_translation':
        formatted_words: str = format_word_items(translation_items, is_translation_items=True)
        formatted_translations: str = format_word_items(word_items)
        correct_translations: list = [translation.get('word').lower() for translation in word_items]

    await state.update_data(wordpair_annotation=wordpair_annotation,
                            formatted_words=formatted_words,
                            formatted_translations=formatted_translations,
                            wordpair_idx=wordpair_idx,
                            correct_translations=correct_translations)

    kb: InlineKeyboardMarkup = get_kb_process_training()  # Клавіатура для тренування
    msg_enter_translation: str = format_training_message(vocab_name=vocab_name,
                                                         training_mode=current_training_mode,
                                                         training_count=current_training_count,
                                                         number_errors=training_number_errors,
                                                         word=formatted_words)
    await message.answer(text=msg_enter_translation, reply_markup=kb)

    # Оновлюємо стан на очікування відповіді
    await state.set_state(VocabTraining.waiting_for_translation)


@router.message(VocabTraining.waiting_for_translation)
async def process_translation(message: types.Message, state: FSMContext) -> None:
    """Обробляє переклад, введений користувачем"""
    data_fsm: dict[str, Any] = await state.get_data()

    wordpair_idx = data_fsm.get('wordpair_idx')

    formatted_words = data_fsm.get('formatted_words')
    formatted_translations = data_fsm.get('formatted_translations')

    available_idxs = data_fsm.get('available_idxs', [])  # Список індексів, які ще не були використані
    correct_translations = data_fsm.get('correct_translations')

    # Переклади без анотацій
    print(correct_translations)
    user_translation: str = message.text.strip().lower()  # Введений користувачем переклад
    print(user_translation)
    if user_translation in correct_translations:
        await message.answer(f'Правильно!\n{formatted_words} -> {formatted_translations}')
        available_idxs.remove(wordpair_idx)
        number_correct_answers = data_fsm.get('number_correct_answers', 0)
        await state.update_data(available_idxs=available_idxs,
                                number_correct_answers=number_correct_answers + 1)  # Оновлення індексу
        await send_next_word(message, state)
    else:
        training_number_errors: int = data_fsm.get('training_number_errors', 0)  # Кількість помилок за тренування
        await state.update_data(training_number_errors=training_number_errors + 1)
        await message.answer('Не Правильно!')
        await send_next_word(message, state)


@router.callback_query(F.data == 'skip_word')
async def process_skip_word(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Повторити тренування" під час тренування"""
    await callback.message.delete()

    data_fsm: dict[str, Any] = await state.get_data()
    available_idxs: list = data_fsm.get('available_idxs', [])  # Список індексів, які ще не були використані
    if len(available_idxs) == 1:
        await callback.message.answer('Залишилось одне слово, не можна пропустити!')
    await send_next_word(callback.message, state)


@router.callback_query(F.data == 'show_annotation')
async def process_show_annotation(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Повторити тренування" під час тренування"""
    await callback.message.delete()

    data_fsm: dict[str, Any] = await state.get_data()
    wordpair_annotation: str = data_fsm.get('wordpair_annotation')
    words: str = data_fsm.get('formatted_words')
    await state.update_data(use_current_word=True)
    await callback.message.answer(f'Слово(а): {words}\nАнотація: {wordpair_annotation}')
    await send_next_word(callback.message, state)


@router.callback_query(F.data == 'show_translation')
async def process_show_translation(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Повторити тренування" під час тренування"""
    await callback.message.delete()

    data_fsm: dict[str, Any] = await state.get_data()
    wordpair_annotation: str = data_fsm.get('wordpair_annotation')
    words: str = data_fsm.get('formatted_words')
    translations: str = data_fsm.get('formatted_translations')
    available_idxs: list = data_fsm.get('available_idxs', [])  # Список індексів, які ще не були використані
    wordpair_idx = data_fsm.get('wordpair_idx')
    number_wrong_answers = data_fsm.get('number_wrong_answers', 0)
    await callback.message.answer(f'Слово(а): {words}\nПереклад(и): {translations}\nАнотація: {wordpair_annotation}')
    available_idxs.remove(wordpair_idx)
    await state.update_data(available_idxs=available_idxs,
                            number_wrong_answers=number_wrong_answers + 1)  # Оновлення індексу
    await send_next_word(callback.message, state)


@router.callback_query(F.data == 'repeat_training')
async def process_repeat_training(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Повторити тренування" під час тренування"""
    await callback.message.delete()

    data_fsm: dict[str, Any] = await state.get_data()
    wordpairs_count: int = data_fsm.get('wordpairs_count')

    available_idxs = list(range(wordpairs_count))
    current_training_count: int = data_fsm.get('current_training_count', 1)  # Кількість тренувань поспіль
    start_time_training: datetime = datetime.now()

    await state.update_data(available_idxs=available_idxs,
                            start_time_training=start_time_training,
                            current_training_count=current_training_count + 1)  # Оновлення списку невикористаних індексів
    await send_next_word(callback.message, state)


@router.callback_query(F.data == 'change_training_mode')
async def process_change_training_mode(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Змінити тип тренування" під час тренування"""
    data_fsm: dict[str, Any] = await state.get_data()
    wordpairs_count: int = data_fsm.get('wordpairs_count')

    available_idxs = list(range(wordpairs_count))
    await state.update_data(available_idxs=available_idxs)  # Оновлення списку невикористаних індексів

    kb: InlineKeyboardMarkup = get_kb_all_training()
    vocab_name: str = data_fsm.get('vocab_name')
    msg_choose_training_mode: str = MSG_CHOOSE_TRAINING_MODE.format(name=vocab_name)

    await callback.message.edit_text(text=msg_choose_training_mode, reply_markup=kb)


@router.callback_query(F.data == 'cancel_training')
async def process_cancel_training(callback: types.CallbackQuery) -> None:
    """Відстежує натискання на кнопку "Скасувати" під час тренування.
    Відправляє клавіатуру для підтвердження скасування.
    """
    kb: InlineKeyboardMarkup = get_kb_confirm_cancel_training()
    msg_confirm_cancel_training: str = MSG_CONFIRM_CANCEL_TRAINING

    await callback.message.edit_text(text=msg_confirm_cancel_training, reply_markup=kb)


@router.callback_query(F.data == 'accept_cancel_training')
async def process_accept_cancel_training(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Так" при підтвердженні видалення користувацького словника.
    Мʼяко видаляє користувацький словник, залишаючи всі його звʼязки в БД.
    """
    data_fsm: dict[str, Any] = await state.get_data()
    wordpairs_count: int = data_fsm.get('wordpairs_count')
    number_wrong_answers = data_fsm.get('number_wrong_answers', 0)

    available_idxs = list(range(wordpairs_count))
    await state.update_data(available_idxs=available_idxs,
                            number_wrong_answers=number_wrong_answers + len(available_idxs),
                            training_is_completed=False)  # Оновлення списку невикористаних індексів

    kb: InlineKeyboardMarkup = get_kb_all_training()
    await finish_training(callback.message, state)
    msg_text = 'Ви скасували тренування'
    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.callback_query(F.data == 'decline_cancel_training')
async def process_decline_cancel_training(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Так" при підтвердженні видалення користувацького словника.
    Мʼяко видаляє користувацький словник, залишаючи всі його звʼязки в БД.
    """
    await send_next_word(callback.message, state)


async def finish_training(message: types.Message, state: FSMContext) -> None:
    """Завершення тренування і оновлення статистики у базі даних."""

    # Отримуємо дані зі стану
    data_fsm: dict[str, Any] = await state.get_data()

    user_id: int = message.from_user.id
    vocab_name = data_fsm.get('name')
    vocab_id = data_fsm.get('vocab_id')
    current_training_mode = data_fsm.get('current_training_mode')
    start_time_training = data_fsm.get('start_time_training')
    end_time_training = datetime.now()
    number_correct_answers = data_fsm.get('number_correct_answers', 0)
    number_wrong_answers = data_fsm.get('number_wrong_answers', 0)
    training_is_completed = data_fsm.get('training_is_completed', True)

    # Обчислюємо різницю
    duration_training = end_time_training - start_time_training

    # Кількість хвилин і секунд
    training_time_minutes = duration_training.seconds // 60  # Цілі хвилини
    training_time_seconds = duration_training.seconds % 60   # Залишкові секунди

    with Session() as session:
        training_crud = TrainingCRUD(session)
        training_crud.create_new_training_session(user_id=user_id,
                                                vocabulary_id=vocab_id,
                                                training_mode=current_training_mode,
                                                start_time=start_time_training,
                                                end_time=end_time_training,
                                                number_correct_answers=number_correct_answers,
                                                number_wrong_answers=number_wrong_answers,
                                                is_completed=training_is_completed)

    # Відправляємо повідомлення користувачеві
    await message.answer(
        f"Тренування завершено!\n"
        f'Словник: {vocab_name}'
        f"✅ Правильні відповіді: {number_correct_answers}\n"
        f"❌ Неправильні відповіді: {number_wrong_answers}\n"
        f'Тривалість тренування: {training_time_minutes} хвилин, {training_time_seconds} секунд'
        f"📊 Статистика збережена."
    )
