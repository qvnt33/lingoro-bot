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

    await state.update_data(user_id=user_id)

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
    wordpairs_count: int = vocab_data.get('wordpairs_count')

    logger.info(f'Обраний користувацький словник. Name: {vocab_name}. ID: {vocab_id}')

    msg_choose_training_mode: str = MSG_CHOOSE_TRAINING_MODE.format(name=vocab_name)

    await state.update_data(vocab_id=vocab_id,
                            vocab_name=vocab_name,
                            wordpair_items=wordpair_items,
                            wordpairs_count=wordpairs_count)
    logger.info('Дані словника збережені у FSM-Cache')

    await callback.message.edit_text(text=msg_choose_training_mode, reply_markup=kb)


@router.callback_query(F.data == 'direct_translation')
async def process_btn_direct_translation(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Прямий переклад" під час вибору типу тренування.
    Починає процес тренування та відправляє перше слово для перекладу.
    """
    logger.info('Початок тренування. Тип: Прямий переклад')
    await callback.message.delete()

    data_fsm: dict[str, Any] = await state.get_data()

    wordpairs_count: int = data_fsm.get('wordpairs_count')  # К-сть словникових пар у користувацькому словнику
    start_time_training: datetime = datetime.now()  # Час початку тренування
    available_idxs = list(range(wordpairs_count))  # Список індексів, які ще не були використані

    await state.update_data(current_training_mode='direct_translation',
                            start_time_training=start_time_training,
                            available_idxs=available_idxs)
    logger.info('Початкові дані тренування збережені у FSM-Cache')

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

    # Прапор, використовувати поточне слово чи обрати нове
    is_use_current_word: bool = data_fsm.get('is_use_current_word', False)

    # Список індексів, які ще не були використані
    available_idxs: list = data_fsm.get('available_idxs', [])

    vocab_name: str = data_fsm.get('vocab_name')
    wordpair_items: list[dict] = data_fsm.get('wordpair_items')

    current_training_mode: str = data_fsm.get('current_training_mode')  # Обраний тип тренування

    check_empty_filter = CheckEmptyFilter()

    # Лічильники
    annotation_shown_count: int = data_fsm.get('annotation_shown_count', 0)  # Показів анотацій
    translation_shown_count: int = data_fsm.get('translation_shown_count', 0)  # Показів перекладу
    training_streak_count: int = data_fsm.get('training_streak_count', 0)  # К-сть тренувань поспіль
    wrong_answer_count: int = data_fsm.get('wrong_answer_count', 0)  # К-сть помилок
    correct_answer_count: int = data_fsm.get('correct_answer_count', 0)  # К-сть вірних відповідей

    # Якщо не залишилось невикористаних індексів
    if check_empty_filter.apply(available_idxs):
        await state.update_data(wrong_answer_count=0,
                                training_is_completed=True)

        await finish_training(state)
        await send_training_finish_stats(message, state)
        return

    preview_wordpair_idx: int = data_fsm.get('wordpair_idx', 0)  # Минулий індекс

    if is_use_current_word:
        wordpair_idx: int = preview_wordpair_idx
        await state.update_data(is_use_current_word=False)
    else:
        # Вибір випадкового індексу з тих, що ще не були використані
        wordpair_idx: int = get_random_wordpair_idx(available_idxs, preview_wordpair_idx)
    await state.update_data(wordpair_idx=wordpair_idx)

    wordpair_item: dict[str, Any] = wordpair_items[wordpair_idx]

    # Список всіх слів та перекладів словникової пари з їх транскрипціями
    word_items: list[dict] = wordpair_item.get('words')
    translation_items: list[dict] = wordpair_item.get('translations')

    wordpair_annotation: str = wordpair_item.get('annotation') or 'Відсутня'  # Анотація словникової пари

    if current_training_mode == 'direct_translation':
        formatted_words: str = format_word_items(word_items)
        formatted_translations: str = format_word_items(translation_items, is_translation_items=True)
        correct_translations: list = [translation.get('translation').lower() for translation in translation_items]
    elif current_training_mode == 'reverse_translation':
        formatted_words: str = format_word_items(translation_items, is_translation_items=True)
        formatted_translations: str = format_word_items(word_items)
        correct_translations: list = [translation.get('word').lower() for translation in word_items]

    await state.update_data(wordpair_idx=wordpair_idx,
                            wordpair_annotation=wordpair_annotation,
                            formatted_words=formatted_words,
                            formatted_translations=formatted_translations,
                            correct_translations=correct_translations)

    kb: InlineKeyboardMarkup = get_kb_process_training()  # Клавіатура для тренування
    msg_enter_translation: str = format_training_message(vocab_name=vocab_name,
                                                         training_mode=current_training_mode,
                                                         training_count=training_streak_count,
                                                         number_errors=wrong_answer_count,
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
        correct_answer_count = data_fsm.get('correct_answer_count', 0)
        await state.update_data(available_idxs=available_idxs,
                                correct_answer_count=correct_answer_count + 1)  # Оновлення індексу
        await send_next_word(message, state)
    else:
        wrong_answer_count: int = data_fsm.get('wrong_answer_count', 0)  # К-сть помилок за тренування
        await state.update_data(wrong_answer_count=wrong_answer_count + 1)
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
    await state.update_data(is_use_current_word=True)
    await callback.message.answer(f'Ви обрали показ анотації!\n\nСлово(а): {words}\nАнотація: {wordpair_annotation}')
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
    wrong_answer_count = data_fsm.get('wrong_answer_count', 0)
    await callback.message.answer(f'Ви обрали показ перекладу!\n\nСлово(а): {words}\nПереклад(и): {translations}\nАнотація: {wordpair_annotation}')
    available_idxs.remove(wordpair_idx)
    await state.update_data(available_idxs=available_idxs,
                            wrong_answer_count=wrong_answer_count + 1)  # Оновлення індексу
    await send_next_word(callback.message, state)


@router.callback_query(F.data == 'repeat_training')
async def process_repeat_training(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Повторити тренування" під час тренування"""
    await callback.message.delete()

    data_fsm: dict[str, Any] = await state.get_data()
    wordpairs_count: int = data_fsm.get('wordpairs_count')

    available_idxs = list(range(wordpairs_count))
    training_streak_count: int = data_fsm.get('training_streak_count', 1)  # К-сть тренувань поспіль
    start_time_training: datetime = datetime.now()

    await state.update_data(available_idxs=available_idxs,
                            start_time_training=start_time_training,
                            training_streak_count=training_streak_count + 1)  # Оновлення списку невикористаних індексів
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
    wrong_answer_count = data_fsm.get('wrong_answer_count', 0)

    available_idxs = list(range(wordpairs_count))
    await state.update_data(available_idxs=available_idxs,
                            wrong_answer_count=wrong_answer_count + len(available_idxs),
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


async def finish_training(state: FSMContext) -> None:
    """Завершення тренування: оновлення статистики у базі даних."""

    # Отримуємо дані зі стану
    data_fsm: dict[str, Any] = await state.get_data()

    user_id: int = data_fsm.get('user_id')
    print(user_id)
    vocab_id = data_fsm.get('vocab_id')
    current_training_mode = data_fsm.get('current_training_mode')
    start_time_training = data_fsm.get('start_time_training')
    end_time_training = datetime.now()
    correct_answer_count = data_fsm.get('correct_answer_count', 0)
    wrong_answer_count = data_fsm.get('wrong_answer_count', 0)

    training_is_completed: bool = data_fsm.get('training_is_completed', True)  # Прапор, чи було завершене тренування

    # Лічильники
    annotation_shown_count: int = data_fsm.get('annotation_shown_count', 0)  # Показів анотацій
    translation_shown_count: int = data_fsm.get('translation_shown_count', 0)  # Показів перекладу
    training_streak_count: int = data_fsm.get('training_streak_count', 0)  # К-сть тренувань поспіль
    wrong_answer_count: int = data_fsm.get('wrong_answer_count', 0)  # К-сть помилок
    correct_answer_count: int = data_fsm.get('correct_answer_count', 0)  # К-сть вірних відповідей

    with Session() as session:
        training_crud = TrainingCRUD(session)
        training_crud.create_new_training_session(
            user_id=user_id,
            vocabulary_id=vocab_id,
            training_mode=current_training_mode,
            start_time=start_time_training,
            end_time=end_time_training,
            number_correct_answers=correct_answer_count,
            number_wrong_answers=wrong_answer_count,
            is_completed=training_is_completed)


async def send_training_finish_stats(message: types.Message, state: FSMContext) -> None:
    """Відправляє статистику завершеного тренування користувачеві."""
    # Отримуємо дані зі стану
    data_fsm: dict[str, Any] = await state.get_data()

    kb: InlineKeyboardMarkup = get_kb_finish_training()

    vocab_name = data_fsm.get('vocab_name')
    start_time_training = data_fsm.get('start_time_training')
    end_time_training = datetime.now()
    correct_answer_count = data_fsm.get('correct_answer_count', 0)
    wrong_answer_count = data_fsm.get('wrong_answer_count', 0)

    # Обчислюємо тривалість тренування
    duration_training = end_time_training - start_time_training
    training_time_minutes = duration_training.seconds // 60  # Цілі хвилини
    training_time_seconds = duration_training.seconds % 60  # Залишкові секунди

    # Формуємо повідомлення
    await message.answer(
        f'🎉 Тренування завершено!\n\n'
        f'📚 Словник: {vocab_name}\n'
        f'✅ Правильні відповіді: {correct_answer_count}\n'
        f'❌ Неправильні відповіді: {wrong_answer_count}\n'
        f'⏱ Тривалість тренування: {training_time_minutes} хвилин, {training_time_seconds} секунд\n\n'
        '➡️ Оберіть, що робити далі:',
    reply_markup=kb
    )
