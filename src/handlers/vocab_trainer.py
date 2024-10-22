import logging
from typing import Any, Dict, List

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from db.crud import get_user_vocab_by_user_id, get_wordpairs_by_vocab_id
from db.database import Session
from db.models import User
from src.fsm.states import VocabTraining
from src.keyboards.vocab_base_kb import get_inline_kb_vocab_buttons
from text_data import MSG_ERROR_VOCAB_BASE_EMPTY

router = Router(name='vocab_trainer')


@router.callback_query(F.data == 'vocab_trainer')
async def process_vocab(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Тренування"""
    user_id: int = callback.from_user.id

    with Session() as db:
        vocab_details: dict = get_user_vocab_by_user_id(db, user_id)
        user_vocabs: User | None = get_user_vocab_by_user_id(db, user_id, is_all=True)  # Словники користувача

        is_vocab_base_empty: bool = get_user_vocab_by_user_id(db, user_id) is None

    vocab_name: str = vocab_details.name

    if is_vocab_base_empty:
        msg_finally: str = MSG_ERROR_VOCAB_BASE_EMPTY
    else:
        msg_finally: str = f'Ви обрали словник: "{vocab_name}"\nОберіть тип, будь-ласка, тип тренування.'

    # Клавіатура для відображення словників
    kb: InlineKeyboardMarkup = get_inline_kb_vocab_buttons(user_vocabs, is_with_create_vocab=False)

    current_state = 'VocabTrainState'  # Стан FSM
    await state.update_data(current_state=current_state)  # Збереження поточного стану FSM

    await callback.message.edit_text(text=msg_finally, reply_markup=kb)


@router.callback_query(F.data == 'direct_translation')
async def process_btn_direct_translation(callback: CallbackQuery, state: FSMContext) -> None:
    """Ініціалізація тренування та збереження даних в кеш"""
    data_fsm: Dict[str, Any] = await state.get_data()
    vocab_id: int = data_fsm.get('vocab_id')

    with Session() as db:
        vocab_details: List[Dict] = get_wordpairs_by_vocab_id(db, vocab_id)

        vocab_data_words = vocab_details['words']
        vocab_data_translations = vocab_details['translations']
        vocab_annotation = vocab_details['annotation']

    await state.update_data(vocab_data_words=vocab_data_words)
    await state.update_data(vocab_data_translations=vocab_data_translations)
    await state.update_data(vocab_annotation=vocab_annotation)

    await state.update_data(flag_training='direct_translation')

    # Запускаємо перше слово для перекладу
    await send_next_word(callback, state)


async def send_next_word(callback: CallbackQuery, state: FSMContext) -> None:
    """Надсилає наступне слово для перекладу"""
    data_fsm: Dict[str, Any] = await state.get_data()
    vocab_details: List[Dict] = data_fsm.get('vocab_details')

    flag_training: List[Dict] = data_fsm.get('flag_training')
    vocab_data_words: List[Dict] = data_fsm.get('vocab_data_words')
    vocab_data_translations: List[Dict] = data_fsm.get('vocab_data_translations')


    # Якщо словникові пари закінчилися
    if len(vocab_details) == 0:
        await callback.message.answer('Вітаємо! Ви успішно завершили тренування.')
        return

    # Отримуємо поточну словникову пару для перекладу
    current_word_idx = data_fsm.get('current_word_idx', 0)
    wordpair_data = vocab_details[current_word_idx]

    # Підготовка даних для користувача
    words_lst = wordpair_data['words']
    formatted_word = []

    for word, transcription in words_lst:
        formatted_word.append(f'{word} [{transcription}]')
    await callback.message.answer(f'Перекладіть слово: {", ".join(formatted_word)}')

    fsm_state: State = VocabTraining.waiting_for_translation  # FSM стан очікування перекладу
    await state.set_state(fsm_state)  # Переведення у новий FSM ста

    await state.update_data(current_word_idx=current_word_idx)


@router.message(VocabTraining.waiting_for_translation)
async def process_translation(message: Message, state: FSMContext) -> None:
    """Обробляє переклад, введений користувачем"""
    data_fsm: Dict[str, Any] = await state.get_data()
    vocab_details: List[Dict] = data_fsm.get('vocab_details')
    current_word_idx = data_fsm.get('current_word_idx', 0)

    wordpair_data = vocab_details[current_word_idx]

    await state.update_data(wordpair_data_old=wordpair_data)  # Додавання ID обраного словника

    # Переклади без анотацій
    correct_translations = [translation[0].lower() for translation in wordpair_data['translations']]

    user_translation = message.text.strip().lower()

    if user_translation == user_translation in correct_translations:
        await message.answer("Правильно!")
        # Видаляємо цю словникову пару з кешу
        vocab_details.pop(current_word_idx)

        # Оновлюємо кеш
        await state.update_data(vocab_details=vocab_details)

        # Якщо словникові пари закінчилися
        if not vocab_details:
            await message.answer("Тренування завершено! Ви переклали всі слова.")
            return
    else:
        await message.answer(f"Неправильно. Правильний переклад: {correct_translation}")

    # Надсилаємо наступне слово для перекладу
    await send_next_word(message, state)
