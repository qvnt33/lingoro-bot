import random
from typing import Any, Dict, List

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from db.crud import get_wordpairs_by_vocab_id
from db.database import Session
from db.models import User
from src.fsm.states import VocabTraining
from src.keyboards.vocab_trainer_kb import get_inline_kb_all_training, get_inline_kb_process_training
from text_data import MSG_ERROR_VOCAB_BASE_EMPTY

router = Router(name='vocab_trainer')


@router.callback_query(F.data == 'vocab_trainer')
async def process_vocab(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Тренування"""
    user_id: int = callback.from_user.id

    with Session() as db:
        get_user_vocab_by_user_id = 1 # !trash
        vocab_details: dict = get_user_vocab_by_user_id(db, user_id)
        user_vocabs: User | None = get_user_vocab_by_user_id(db, user_id, is_all=True)  # Словники користувача

        is_vocab_base_empty: bool = get_user_vocab_by_user_id(db, user_id) is None

        if is_vocab_base_empty:
            msg_finally: str = MSG_ERROR_VOCAB_BASE_EMPTY
        else:
            vocab_name: str = vocab_details.name
            msg_finally: str = f'Ви обрали словник: "{vocab_name}"\nОберіть тип, будь-ласка, тип тренування.'

    # Клавіатура для відображення словників
    # kb: InlineKeyboardMarkup = get_inline_kb_vocab_selection(user_vocabs, is_with_create_vocab=False)

    current_state = 'VocabTrainState'  # Стан FSM
    await state.update_data(current_state=current_state)  # Збереження поточного стану FSM

    # await callback.message.edit_text(text=msg_finally, reply_markup=kb)


@router.callback_query(F.data == 'reverse_translation')
async def process_btn_reverse_translation(callback: CallbackQuery, state: FSMContext) -> None:
    """Ініціалізація тренування і збереження даних у FSM"""
    data_fsm: Dict[str, Any] = await state.get_data()
    vocab_id: int = data_fsm.get('vocab_id')

    with Session() as db:
        vocab_details: List[Dict] = get_wordpairs_by_vocab_id(db, vocab_id)

    # Список індексів, які ще не були використані
    available_indices = list(range(len(vocab_details)))

    # Збереження всіх деталей у стані FSM
    await state.update_data(vocab_details=vocab_details, available_indices=available_indices, flag_training='reverse_translation')

    # Надсилаємо першу пару на переклад
    await send_next_word(callback.message, state)


@router.callback_query(F.data == 'direct_translation')
async def process_btn_direct_translation(callback: CallbackQuery, state: FSMContext) -> None:
    """Ініціалізація тренування і збереження даних у FSM"""
    data_fsm: Dict[str, Any] = await state.get_data()
    vocab_id: int = data_fsm.get('vocab_id')

    with Session() as db:
        vocab_details: List[Dict] = get_wordpairs_by_vocab_id(db, vocab_id)

    # Список індексів, які ще не були використані
    available_indices = list(range(len(vocab_details)))

    # Збереження всіх деталей у стані FSM
    await state.update_data(vocab_details=vocab_details, available_indices=available_indices, flag_training='direct_translation')

    # Надсилаємо першу пару на переклад
    await send_next_word(callback.message, state)


async def send_next_word(message: Message, state: FSMContext) -> None:
    """Надсилає наступне слово для перекладу"""
    data_fsm: Dict[str, Any] = await state.get_data()

    vocab_details: List[Dict] = data_fsm.get('vocab_details')
    available_indices = data_fsm.get('available_indices', [])  # Список індексів, які ще не були використані
    old_wordpair_idx = data_fsm.get('wordpair_idx', 1)  # Минулий індекс
    flag_training = data_fsm.get('flag_training')  # Флаг тренування

    # Вибір випадкового індексу з тих, що ще не використані
    if len(available_indices) == 1:
        wordpair_idx = available_indices[0]
    elif len(available_indices) >= 1:
        while True:
            wordpair_idx = random.choice(available_indices)  # Індекс словникової пари
            # Якщо індекс не такий як минулий
            if wordpair_idx != old_wordpair_idx:
                await state.update_data(available_indices=available_indices)  # Оновлення індексу
                break
    else:
        kb: InlineKeyboardMarkup = get_inline_kb_all_training()
        await message.answer(text='Всі словникові пари переведені. Тренування завершено!', reply_markup=kb)
        vocab_id: int = data_fsm.get('vocab_id')
        await state.clear()  # Очищення FSM-кеш та FSM-стану
        await state.update_data(vocab_id=vocab_id)  # Оновлення індексу
        return

    wordpair_data = vocab_details[wordpair_idx]
    if flag_training == 'direct_translation':
        formatted_word = ', '.join(f'{word} [{transcription}]' if transcription else word for word, transcription in wordpair_data['words'])
        formatted_translation = ', '.join(f'{word} [{transcription}]' if transcription else word for word, transcription in wordpair_data['translations'])
        correct_translations = [translation[0].lower() for translation in wordpair_data['translations']]
    elif flag_training == 'reverse_translation':
        formatted_translation = ', '.join(f'{word} [{transcription}]' if transcription else word for word, transcription in wordpair_data['words'])
        formatted_word = ', '.join(f'{word} [{transcription}]' if transcription else word for word, transcription in wordpair_data['translations'])
        correct_translations = [translation[0].lower() for translation in wordpair_data['words']]

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

    vocab_details: List[Dict] = data_fsm.get('vocab_details')
    wordpair_idx = data_fsm.get('wordpair_idx')

    formatted_word = data_fsm.get('formatted_word')
    formatted_translation = data_fsm.get('formatted_translation')

    available_indices = data_fsm.get('available_indices', [])  # Список індексів, які ще не були використані
    correct_translations = data_fsm.get('correct_translations')

    wordpair_data = vocab_details[wordpair_idx]
    kb: InlineKeyboardMarkup = get_inline_kb_process_training()  # Клавіатура для тренування

    # Переклади без анотацій
    print(correct_translations)
    user_translation: str = message.text.strip().lower()  # Введений користувачем переклад
    print(user_translation)
    if user_translation in correct_translations:
        await message.answer(f'Правильно!\n{formatted_word} -> {formatted_translation}')
        available_indices.remove(wordpair_idx)
        await state.update_data(available_indices=available_indices)  # Оновлення індексу
        await send_next_word(message, state)
    else:
        await message.answer('Не Правильно!')
        await send_next_word(message, state)


@router.callback_query(F.data == 'cancel_training')
async def process_cancel_training(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Скасувати" під час тренування"""
    data_fsm: Dict[str, Any] = await state.get_data()
    vocab_id: int = data_fsm.get('vocab_id')
    await state.clear()  # Очищення FSM-кеш та FSM-стану
    await state.update_data(vocab_id=vocab_id)  # Оновлення індексу
    await process_vocab(callback, state)



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
