import logging
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
    get_kb_confirm_cancel_training,
    get_kb_finish_training,
    get_kb_training_actions,
    get_kb_training_modes,
    get_kb_vocab_selection_training,
)
from text_data import (
    MSG_CHOOSE_TRAINING_MODE,
    MSG_CHOOSE_VOCAB_FOR_TRAINING,
    MSG_CONFIRM_CANCEL_TRAINING,
    MSG_CORRECT_ANSWER,
    MSG_INFO_VOCAB_BASE_EMPTY_FOR_TRAINING,
    MSG_LEFT_ONE_WORD_TRAINING,
    MSG_SHOW_WORDPAIR_ANNOTATION,
    MSG_SHOW_WORDPAIR_TRANSLATION,
    MSG_WRONG_ANSWER,
)
from tools.vocab_trainer_utils import (
    format_training_process_message,
    format_training_summary_message,
    get_random_wordpair_idx,
)
from tools.wordpair_utils import format_word_items

router = Router(name='vocab_trainer')
logger: logging.Logger = logging.getLogger(__name__)


@router.callback_query(F.data == 'vocab_trainer')
async def process_vocab_trainer(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Тренування" у головному меню.
    Відправляє користувачу користувацькі словники у вигляді кнопок.
    """
    user_id: int = callback.from_user.id

    logger.info(f'Користувач перейшов до розділу "Тренування". USER_ID: {user_id}')

    check_empty_filter = CheckEmptyFilter()

    await state.clear()
    logger.info('FSM стан та FSM-Cache очищено перед запуском розділу "Тренування"')

    await state.update_data(user_id=user_id)

    with Session() as session:
        vocab_crud = VocabCRUD(session)

        # Дані всіх користувацьких словників користувача
        all_vocabs_data: list[dict] = vocab_crud.get_all_vocabs_data(user_id)

    # Якщо в БД користувача немає користувацьких словників
    if check_empty_filter.apply(all_vocabs_data):
        kb: InlineKeyboardMarkup = get_kb_vocab_selection_training(all_vocabs_data[::-1], is_with_btn_vocab_base=True)
        msg_text: str = MSG_INFO_VOCAB_BASE_EMPTY_FOR_TRAINING
    else:
        kb: InlineKeyboardMarkup = get_kb_vocab_selection_training(all_vocabs_data[::-1])
        msg_text: str = MSG_CHOOSE_VOCAB_FOR_TRAINING
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

    kb: InlineKeyboardMarkup = get_kb_training_modes()

    vocab_name: str = vocab_data.get('name')
    total_wordpairs_count: int = vocab_data.get('wordpairs_count')  # К-сть словникових пар у користувацькому словнику

    logger.info(f'Обраний користувацький словник. Назва: "{vocab_name}". ID: {vocab_id}')

    msg_choose_training_mode: str = MSG_CHOOSE_TRAINING_MODE.format(name=vocab_name)

    await state.update_data(vocab_id=vocab_id,
                            vocab_name=vocab_name,
                            wordpair_items=wordpair_items,
                            total_wordpairs_count=total_wordpairs_count)
    logger.info('Дані словника збережені у FSM-Cache')

    await callback.message.edit_text(text=msg_choose_training_mode, reply_markup=kb)


@router.callback_query(F.data == 'direct_translation')
async def process_direct_translation(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Прямий переклад" під час вибору типу тренування.
    Починає процес тренування та відправляє перше слово для перекладу.
    """
    logger.info('Початок тренування. Тип: "Прямий переклад"')
    await callback.message.delete()

    data_fsm: dict[str, Any] = await state.get_data()

    total_wordpairs_count: int = data_fsm.get('total_wordpairs_count')
    available_idxs: list = list(range(total_wordpairs_count))  # Список індексів словникових пар
    start_time_training: datetime = datetime.now()  # Час початку тренування

    await state.update_data(training_mode='direct_translation',
                            start_time_training=start_time_training,
                            available_idxs=available_idxs)
    logger.info('Початкові дані тренування збережені у FSM-Cache')

    await send_next_word(callback.message, state)


@router.callback_query(F.data == 'reverse_translation')
async def process_reverse_translation(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Зворотній переклад" під час вибору типу тренування.
    Починає процес тренування та відправляє перше слово для перекладу.
    """
    logger.info('Початок тренування. Тип: "Зворотній переклад"')
    await callback.message.delete()

    data_fsm: dict[str, Any] = await state.get_data()

    total_wordpairs_count: int = data_fsm.get('total_wordpairs_count')
    available_idxs: list = list(range(total_wordpairs_count))  # Список індексів словникових пар
    start_time_training: datetime = datetime.now()  # Час початку тренування

    await state.update_data(training_mode='reverse_translation',
                            start_time_training=start_time_training,
                            available_idxs=available_idxs)
    logger.info('Початкові дані тренування збережені у FSM-Cache')

    await send_next_word(callback.message, state)


@router.callback_query(F.data == 'change_training_mode')
async def process_change_training_mode(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Змінити тип тренування" під час тренування.
    Відправляє клавіатуру зі списком типів словникових тренувань.
    """
    logger.info('Зміна типу тренування')

    data_fsm: dict[str, Any] = await state.get_data()
    vocab_name: str = data_fsm.get('vocab_name')

    kb: InlineKeyboardMarkup = get_kb_training_modes()
    msg_choose_training_mode: str = MSG_CHOOSE_TRAINING_MODE.format(name=vocab_name)

    await callback.message.edit_text(text=msg_choose_training_mode, reply_markup=kb)


def get_wordpair_idx_for_training(available_idxs: list, preview_wordpair_idx: int, is_use_current_words: bool) -> int:
    """Повертає індекс словникової пари для тренування.

    Notes:
        Якщо is_use_current_words=True, то повертається попередній індекс,
        в іншому разі випадковий із списку невикористаних.

    Args:
        available_idxs (list): Список індексів, які ще не були використані.
        preview_wordpair_idx (int): Минулий індекс.
        is_use_current_words (bool): Прапор, використовувати поточне слово(а) чи обрати нове.
    """
    if is_use_current_words:
        return preview_wordpair_idx

    # Вибір випадкового індексу з тих, що ще не були використані
    return get_random_wordpair_idx(available_idxs, preview_wordpair_idx)


async def send_next_word(message: types.Message, state: FSMContext) -> None:
    """Відправляє наступне слово для перекладу"""
    data_fsm: dict[str, Any] = await state.get_data()

    available_idxs: list = data_fsm.get('available_idxs')  # Список індексів, які ще не були використані

    # Якщо не залишилось невикористаних індексів
    check_empty_filter = CheckEmptyFilter()
    if check_empty_filter.apply(available_idxs):
        await state.update_data(is_training_completed=True)
        await send_training_finish_stats(message, state)
        await finish_training(state)
        return

    vocab_name: str = data_fsm.get('vocab_name')
    wordpair_items: list[dict] = data_fsm.get('wordpair_items')

    training_mode: str = data_fsm.get('training_mode')  # Обраний тип тренування
    preview_wordpair_idx: int = data_fsm.get('wordpair_idx', 0)  # Минулий індекс

    # Прапор, використовувати поточне слово(а) чи обрати нове
    is_use_current_words: bool = data_fsm.get('is_use_current_words', False)
    if is_use_current_words:
        await state.update_data(is_use_current_words=False)

    wordpair_idx: int = await get_wordpair_idx_for_training(available_idxs,
                                                            preview_wordpair_idx,
                                                            is_use_current_words)

    await state.update_data(wordpair_idx=wordpair_idx)
    logger.info('Оновлення нового індексу словникової пари у FSM-Cache')

    wordpair_item: dict[str, Any] = wordpair_items[wordpair_idx]

    # Список всіх слів та перекладів словникової пари з їх транскрипціями
    word_items: list[dict] = wordpair_item.get('words')
    translation_items: list[dict] = wordpair_item.get('translations')
    wordpair_annotation: str = wordpair_item.get('annotation') or 'Відсутня'  # Анотація словникової пари

    if training_mode == 'direct_translation':
        training_mode_name = 'Прямий переклад (W -> T)'
        formatted_words: str = format_word_items(word_items)
        formatted_translations: str = format_word_items(translation_items, is_translation_items=True)
        correct_translations: list[str] = [translation.get('translation').lower() for translation in translation_items]
    elif training_mode == 'reverse_translation':
        training_mode_name = 'Зворотній переклад (T -> W)'
        formatted_words: str = format_word_items(translation_items, is_translation_items=True)
        formatted_translations: str = format_word_items(word_items)
        correct_translations: list[str] = [translation.get('word').lower() for translation in word_items]

    logger.info(f'Словникова пара для перекладу: "{formatted_words}" -> "{formatted_translations}"')

    total_wordpairs_count: int = data_fsm.get('total_wordpairs_count')
    wordpairs_left: int = total_wordpairs_count - len(available_idxs)  # Скільки залишилось словникових пар

    kb: InlineKeyboardMarkup = get_kb_training_actions()  # Клавіатура з діями під час тренування
    msg_enter_translation: str = format_training_process_message(vocab_name=vocab_name,
                                                                 training_mode=training_mode_name,
                                                                 wordpairs_left=wordpairs_left,
                                                                 total_wordpairs_count=total_wordpairs_count,
                                                                 words=formatted_words)

    await state.update_data(wordpair_annotation=wordpair_annotation,
                            formatted_words=formatted_words,
                            formatted_translations=formatted_translations,
                            correct_translations=correct_translations,
                            training_mode_name=training_mode_name)
    logger.info('Дані словникової пари для перекладу збережені у FSM-Cache')

    await message.answer(text=msg_enter_translation, reply_markup=kb)
    await state.set_state(VocabTraining.waiting_for_translation)


@router.message(VocabTraining.waiting_for_translation)
async def process_check_user_translation(message: types.Message, state: FSMContext) -> None:
    """Обробляє переклад, введений користувачем"""
    data_fsm: dict[str, Any] = await state.get_data()

    wordpair_idx: int = data_fsm.get('wordpair_idx')

    formatted_words: str = data_fsm.get('formatted_words')
    formatted_translations: str = data_fsm.get('formatted_translations')

    available_idxs: list = data_fsm.get('available_idxs', [])  # Список індексів, які ще не були використані
    correct_translations: list = data_fsm.get('correct_translations')  # Переклади у нижньому регістри без анотацій

    user_translation: str = message.text.strip()  # Введений користувачем переклад
    logger.info(f'Введений переклад: "{user_translation}"')

    if user_translation.lower() in correct_translations:
        await message.answer(MSG_CORRECT_ANSWER.format(words=formatted_words, translations=formatted_translations))
        logger.info('Переклад ВІРНИЙ')

        available_idxs.remove(wordpair_idx)
        await state.update_data(available_idxs=available_idxs)
        logger.info('Видалення індексу коректного перекладу та оновлення списку невикористаних індексів у FSM-Cache')

        correct_answer_count: int = data_fsm.get('correct_answer_count', 0)
        await state.update_data(correct_answer_count=correct_answer_count + 1)
        logger.info('Оновлення к-сть коректних відповідей у FSM-Cache')

        await send_next_word(message, state)
    else:
        await message.answer(MSG_WRONG_ANSWER.format(words=formatted_words, user_translation=user_translation))
        logger.info('Переклад НЕ ВІРНИЙ')

        wrong_answer_count: int = data_fsm.get('wrong_answer_count', 0)
        await state.update_data(wrong_answer_count=wrong_answer_count + 1)
        logger.info('Оновлення к-сть некоректних відповідей у FSM-Cache')

        await send_next_word(message, state)


@router.callback_query(F.data == 'skip_word')
async def process_skip_word(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Пропустити" під час тренування"""
    logger.info('Обраний пропуск словникової пари')

    await callback.message.delete()

    data_fsm: dict[str, Any] = await state.get_data()

    # Якщо залишилось остання словникова пара для перекладу
    available_idxs: list = data_fsm.get('available_idxs')
    if len(available_idxs) == 1:
        logger.info('Залишилась остання словникова пара. Пропуск неможливий')
        await callback.message.answer(text=MSG_LEFT_ONE_WORD_TRAINING)
    await send_next_word(callback.message, state)


@router.callback_query(F.data == 'show_annotation')
async def process_show_annotation(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Показати анотацію" під час тренування"""
    logger.info('Обраний показ анотації словникової пари')

    await callback.message.delete()

    data_fsm: dict[str, Any] = await state.get_data()

    wordpair_annotation: str = data_fsm.get('wordpair_annotation')
    formatted_words: str = data_fsm.get('formatted_words')
    annotation_shown_count: int = data_fsm.get('annotation_shown_count', 0)  # К-сть показів анотацій

    await state.update_data(is_use_current_words=True)
    logger.info('Оновлення прапора "використання поточного слова (is_use_current_words)" на True у FSM-Cache. '
                'Щоб після показу анотації, потрібно було перекласти поточне слово')

    await state.update_data(annotation_shown_count=annotation_shown_count + 1)
    logger.info('Оновлення к-сть показів анотацій у FSM-Cache')

    msg_show_annotation: str = MSG_SHOW_WORDPAIR_ANNOTATION.format(words=formatted_words,
                                                                   annotation=wordpair_annotation)
    await callback.message.answer(msg_show_annotation)
    await send_next_word(callback.message, state)


@router.callback_query(F.data == 'show_translation')
async def process_show_translation(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Показати переклад" під час тренування"""
    logger.info('Обраний показ перекладу словникової пари')

    await callback.message.delete()

    data_fsm: dict[str, Any] = await state.get_data()

    formatted_words: str = data_fsm.get('formatted_words')
    formatted_translations: str = data_fsm.get('formatted_translations')
    wordpair_annotation: str = data_fsm.get('wordpair_annotation')

    available_idxs: list = data_fsm.get('available_idxs')
    wordpair_idx: int = data_fsm.get('wordpair_idx')

    translation_shown_count: int = data_fsm.get('translation_shown_count', 0)

    available_idxs.remove(wordpair_idx)
    await state.update_data(available_idxs=available_idxs)
    logger.info('Видалення індексу показаного перекладу словникової пари та '
                'оновлення списку невикористаних індексів у FSM-Cache')

    await state.update_data(translation_shown_count=translation_shown_count + 1)
    logger.info('Оновлення к-сть показаних перекладів у FSM-Cache')

    msg_show_translation: str = MSG_SHOW_WORDPAIR_TRANSLATION.format(words=formatted_words,
                                                                     translations=formatted_translations,
                                                                     annotation=wordpair_annotation)
    await callback.message.answer(msg_show_translation)

    await send_next_word(callback.message, state)


@router.callback_query(F.data == 'repeat_training')
async def process_repeat_training(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Повторити тренування" після проходження тренування"""
    logger.info('Обрано повторення тренування після його проходження')

    await callback.message.delete()

    data_fsm: dict[str, Any] = await state.get_data()

    training_streak_count: int = data_fsm.get('training_streak_count', 0)  # К-сть тренувань поспіль
    start_time_training: datetime = datetime.now()  # Час початку тренування

    await state.update_data(start_time_training=start_time_training,
                            training_streak_count=training_streak_count + 1)
    logger.info('Оновлення к-сть тренувань поспіль та час початку тренування у FSM-Cache')

    await send_next_word(callback.message, state)


@router.callback_query(F.data == 'cancel_training')
async def process_cancel_training(callback: types.CallbackQuery) -> None:
    """Відстежує натискання на кнопку "Завершити тренування" під час тренування.
    Відправляє клавіатуру для підтвердження завершення.
    """
    logger.info('Обрано завершення тренування, під час тренування')

    kb: InlineKeyboardMarkup = get_kb_confirm_cancel_training()
    msg_confirm_cancel_training: str = MSG_CONFIRM_CANCEL_TRAINING

    await callback.message.edit_text(text=msg_confirm_cancel_training, reply_markup=kb)


@router.callback_query(F.data == 'accept_cancel_training')
async def process_accept_cancel_training(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Так" при підтвердженні дострокового завершення тренування.
    Завершує тренування.
    Відправляє клавіатуру зі списком типів тренування.
    """
    logger.info('Дострокове завершення тренування')

    data_fsm: dict[str, Any] = await state.get_data()
    vocab_name: str = data_fsm.get('vocab_name')

    await state.update_data(is_training_completed=False)  # Оновлення списку невикористаних індексів
    logger.info('Оновлення прапора "тренування було завершено (is_training_completed)" на False у FSM-Cache. ')

    await finish_training(state)

    kb: InlineKeyboardMarkup = get_kb_training_modes()
    msg_choose_training_mode: str = MSG_CHOOSE_TRAINING_MODE.format(name=vocab_name)

    await callback.message.edit_text(text=msg_choose_training_mode, reply_markup=kb)


@router.callback_query(F.data == 'decline_cancel_training')
async def process_decline_cancel_training(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Ні" при підтвердженні дострокового завершення тренування.
    Продовжує тренування.
    Відправляє нове слово для перекладу.
    """
    logger.info('Продовження тренування')

    await callback.message.delete()

    await send_next_word(callback.message, state)


async def finish_training(state: FSMContext) -> None:
    """Завершення тренування.
    Додає до БД інформацію про сесію тренування та анулює лічильники тренування.
    """
    data_fsm: dict[str, Any] = await state.get_data()

    user_id: int = data_fsm.get('user_id')
    vocab_id: int = data_fsm.get('vocab_id')

    training_mode: str = data_fsm.get('training_mode')
    is_training_completed: bool = data_fsm.get('is_training_completed', True)

    start_time_training: datetime = data_fsm.get('start_time_training')
    end_time_training: datetime = datetime.now()

    wrong_answer_count: int = data_fsm.get('wrong_answer_count', 0)
    correct_answer_count: int = data_fsm.get('correct_answer_count', 0)

    with Session() as session:
        training_crud = TrainingCRUD(session)
        training_crud.create_new_training_session(
            user_id=user_id,
            vocabulary_id=vocab_id,
            training_mode=training_mode,
            start_time=start_time_training,
            end_time=end_time_training,
            number_correct_answers=correct_answer_count,
            number_wrong_answers=wrong_answer_count,
            is_completed=is_training_completed)
        logger.info('В БД додано інформацію про сесію тренування')

    total_wordpairs_count: int = data_fsm.get('total_wordpairs_count')
    available_idxs = list(range(total_wordpairs_count))

    await state.update_data(available_idxs=available_idxs)
    logger.info('Оновлення списку невикористаних індексів словникових пар у FSM-Cache')

    await state.update_data(correct_answer_count=0,
                            wrong_answer_count=0,
                            translation_shown_count=0)
    logger.info('Анулювання лічильників тренування у FSM-Cache')


async def send_training_finish_stats(message: types.Message, state: FSMContext) -> None:
    """Відправляє статистику завершеного тренування користувачеві"""
    data_fsm: dict[str, Any] = await state.get_data()

    kb: InlineKeyboardMarkup = get_kb_finish_training()

    vocab_name: str = data_fsm.get('vocab_name')
    start_time_training: datetime = data_fsm.get('start_time_training')
    end_time_training: datetime = datetime.now()
    training_mode_name: str = data_fsm.get('training_mode')  # Назва режиму тренування
    training_streak_count: int = data_fsm.get('training_streak_count', 1)  # К-сть тренувань поспіль
    correct_answer_count: int = data_fsm.get('correct_answer_count', 0)  # К-сть переведених слів
    wrong_answer_count: int = data_fsm.get('wrong_answer_count', 0)  # К-сть помилок
    annotation_shown_count: int = data_fsm.get('annotation_shown_count', 0)  # Показів анотацій
    translation_shown_count: int = data_fsm.get('translation_shown_count', 0)  # Показів перекладу

    # Обчислення тривалості тренування
    duration_training: datetime.timedelta = end_time_training - start_time_training
    training_time_minutes: int = duration_training.seconds // 60  # Цілі хвилини
    training_time_seconds: int = duration_training.seconds % 60  # Залишкові секунди

    summary_message: str = format_training_summary_message(vocab_name=vocab_name,
                                                           training_mode=training_mode_name,
                                                           training_streak_count=training_streak_count,
                                                           correct_answer_count=correct_answer_count,
                                                           wrong_answer_count=wrong_answer_count,
                                                           annotation_shown_count=annotation_shown_count,
                                                           translation_shown_count=translation_shown_count,
                                                           training_time_minutes=training_time_minutes,
                                                           training_time_seconds=training_time_seconds)

    await message.answer(text=summary_message, reply_markup=kb)
