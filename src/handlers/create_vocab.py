import logging
from typing import Any, Dict

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from config import DEFAULT_VOCAB_DESCRIPTION
from db.crud import add_vocab_to_db
from db.database import Session
from src.fsm.states import VocabCreation
from src.keyboards.create_vocab_kb import (
    get_inline_kb_create_vocab_name,
    get_kb_confirm_cancel,
    get_kb_create_vocab_description,
    get_kb_create_wordpairs,
)
from src.keyboards.menu_kb import get_inline_kb_menu
from src.validators.vocab.vocab_name_validator import VocabNameValidator
from src.validators.vocab.vocab_description_validator import VocabDescriptionValidator
from src.validators.wordpair.wordpair_validator import WordPairValidator
from text_data import (
    MSG_ADDED_WORDPAIRS,
    MSG_CONFIRM_CANCEL_CREATE_VOCAB,
    MSG_ENTER_NEW_VOCAB_NAME,
    MSG_ENTER_VOCAB_NAME,
    MSG_ERROR_NO_ADD_WORDPAIRS,
    MSG_ERROR_NO_VALID_WORDPAIRS,
    MSG_ERROR_VOCAB_SAME_NAME,
    MSG_MENU,
    MSG_NO_ADDED_WORDPAIRS,
    MSG_NO_ERRORS_WORDPAIRS,
    MSG_ENTER_VOCAB_DESCRIPTION,
    MSG_SUCCESS_VOCAB_DESCRIPTION_CREATED,
    MSG_SUCCESS_VOCAB_SAVED_TO_DB,
    MSG_VOCAB_NAME_ERRORS,
    MSG_VOCAB_DESCRIPTION_ERRORS,
    MSG_ENTER_WORDPAIRS,
    MSG_VOCAB_WORDPAIRS_SAVED_SMALL_INSTRUCTIONS,
)
from tools.message_formatter import add_vocab_data_to_message

router = Router(name='create_vocab')


async def save_current_fsm_state(state: FSMContext, new_state: State) -> None:
    """Зберігає поточний стан FSM та оновлює FSM-Cache зі значенням нового стану"""
    await state.set_state(new_state)
    logging.info(f'FSM стан змінено на "{new_state}"')

    await state.update_data(current_stage=new_state)
    logging.info(f'FSM стан "{new_state}" збережений у FSM-Cache, як поточний стан')


@router.callback_query(F.data == 'create_vocab')
async def process_create_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    logging.info(f'START: Створення словника. USER_ID: {callback.from_user.id}')

    await state.clear()
    logging.info('FSM стан та FSM-Cache очищено')

    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()
    msg_text: str = add_vocab_data_to_message(message=MSG_ENTER_VOCAB_NAME)

    await save_current_fsm_state(state, VocabCreation.waiting_for_vocab_name)

    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.message(VocabCreation.waiting_for_vocab_name)
async def process_create_vocab_name(message: types.Message, state: FSMContext) -> None:
    """Обробляє назву словника, яку ввів користувач"""
    data_fsm: dict = await state.get_data()  # Дані з FSM

    vocab_name: str = message.text.strip()  # Введена назва словника (без зайвих пробілів)
    vocab_name_old: str | None = data_fsm.get('vocab_name')  # Поточна назва словника (якщо є)

    logging.info(f'Користувач ввів назву до словника: "{vocab_name}"')

    # Якщо введена назва словника збігається з поточною
    if vocab_name_old is not None and vocab_name.lower() == vocab_name_old.lower():
        logging.warning(f'Назва до словника "{vocab_name}" збігається з поточною')

        # Клавіатура для створення назви словника з кнопкою зберігання назви
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name(is_keep_old_vocab_name=True)
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name_old, message=MSG_ERROR_VOCAB_SAME_NAME)

        await message.answer(text=msg_text, reply_markup=kb)
        return  # Завершення подальшої обробки

    with Session() as session:
        validator_vocab_name = VocabNameValidator(name=vocab_name, user_id=message.from_user.id, db_session=session)

    if validator_vocab_name.is_valid():
        kb: InlineKeyboardMarkup = get_kb_create_vocab_description()  # Клавіатура для створення примітки
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name, message=MSG_ENTER_VOCAB_DESCRIPTION)

        await state.update_data(vocab_name=vocab_name)
        logging.info(f'Назва словника "{vocab_name}" збережена у FSM-Cache')

        await save_current_fsm_state(state, VocabCreation.waiting_for_vocab_description)
    else:
        formatted_errors: str = validator_vocab_name.format_errors()

        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name_old,
                                                   message=MSG_VOCAB_NAME_ERRORS.format(vocab_name=vocab_name,
                                                                                        errors=formatted_errors))
    await message.answer(text=msg_text, reply_markup=kb)


@router.message(VocabCreation.waiting_for_vocab_description)
async def process_vocab_description(message: types.Message, state: FSMContext) -> None:
    """Обробляє примітку до словника, яку ввів користувач"""
    data_fsm: dict = await state.get_data()  # Дані з FSM

    vocab_name: Any | None = data_fsm.get('vocab_name')
    vocab_description: str = message.text.strip()  # Примітка до словника, введена користувачем (без зайвих пробілів)

    kb: InlineKeyboardMarkup = get_kb_create_wordpairs()  # Клавіатура для створення примітки

    logging.info(f'Користувач ввів примітку "{vocab_description}" до словника "{vocab_name}"')

    validator_note = VocabDescriptionValidator(note=vocab_description)

    # Якщо примітка коректна
    if validator_note.is_valid():
        message_msg: str = '\n\n'.join([MSG_SUCCESS_VOCAB_DESCRIPTION_CREATED, MSG_ENTER_WORDPAIRS])

        msg_final: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                vocab_description=vocab_description,
                                                message=message_msg)

        await state.update_data(vocab_description=vocab_description)  # Збереження примітки в кеш FSM
        logging.info(f'Примітка "{vocab_description}" до словника "{vocab_name}" збережена у FSM-кеш')

        await save_current_fsm_state(state, VocabCreation.waiting_for_wordpairs)
    else:
        formatted_errors: str = validator_note.format_errors()  # Відформатований список помилок
        msg_final: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                   message=MSG_VOCAB_DESCRIPTION_ERRORS.format(vocab_description=vocab_description,
                                                                                     vocab_name=vocab_name,
                                                                                     errors=formatted_errors))
    await message.answer(text=msg_final, reply_markup=kb)


@router.message(VocabCreation.waiting_for_wordpairs)
async def process_wordpairs(message: types.Message, state: FSMContext) -> None:
    """Обробляє словникові пари, введені користувачем"""
    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM

    vocab_name: str = data_fsm.get('vocab_name')
    vocab_description: str = data_fsm.get('vocab_description')

    wordpairs: str = message.text.strip()  # Словникові пари, введенні користувачем  (без зайвих пробілів)
    logging.info(f'Введено словникові пари "{wordpairs}" до словника "{vocab_name}"')

    wordpairs_lst: list[str] = wordpairs.split('\n')  # Список словникових пар

    valid_wordpairs_lst: list[str] = []  # Список коректних словникових пар
    invalid_wordpairs_lst: list[dict] = []  # Список не коректних словникових пар

    validated_data_wordpairs: Any | list = data_fsm.get('validated_data_wordpairs') or []  # Всі дані словникових пар

    kb: InlineKeyboardMarkup = get_kb_create_wordpairs()  # Клавіатура для створення словникових пар

    for wordpair in wordpairs_lst:
        validator_wordpair = WordPairValidator(wordpair=wordpair, vocab_name=vocab_name)
        is_valid_wordpair: bool = validator_wordpair.is_valid()  # Чи коректна словникова пара

        if is_valid_wordpair:
            logging.info(f'Словникова пара "{wordpair}" коректна')

            valid_wordpairs_lst.append(wordpair)

            validated_data: dict = validator_wordpair.validated_data  # Словник з даними словникової пари
            validated_data_wordpairs.append(validated_data)
        else:
            logging.warning(f'Словникова пара "{wordpair}" некоректна')

            formatted_errors: str = validator_wordpair.format_errors()
            invalid_wordpairs_lst.append({
                'wordpair': wordpair,
                'errors': formatted_errors})

    # Якщо є валідні словникові пар
    if valid_wordpairs_lst:
        joined_valid_wordpairs: str = '\n'.join([f'- {wordpair}' for wordpair in valid_wordpairs_lst])
        valid_msg: str = MSG_ADDED_WORDPAIRS.format(wordpairs=joined_valid_wordpairs)
    else:
        valid_msg = MSG_ERROR_NO_VALID_WORDPAIRS

    # Збереження всіх даних словникових пар в FSM-кеш
    await state.update_data(validated_data_wordpairs=validated_data_wordpairs)

    # Якщо є не валідні словникові пар
    if invalid_wordpairs_lst:
        invalid_msg_parts_lst: list = []
        for wordpair in invalid_wordpairs_lst:
            # Кожна словникова пара та помилки
            sep_invalid_wordpair: str = f'- {wordpair["wordpair"]}\n{wordpair["errors"]}'
            invalid_msg_parts_lst.append(sep_invalid_wordpair)

        joined_invalid_wordpairs: str = '\n'.join(invalid_msg_parts_lst)
        invalid_msg: str = MSG_NO_ADDED_WORDPAIRS.format(wordpairs=joined_invalid_wordpairs)
    else:
        invalid_msg: str = MSG_NO_ERRORS_WORDPAIRS

    msg_message = MSG_VOCAB_WORDPAIRS_SAVED_SMALL_INSTRUCTIONS
    msg_for_status: str = '\n\n'.join((valid_msg, invalid_msg, msg_message))

    msg_final: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                            vocab_description=vocab_description,
                                            message=msg_for_status)

    await message.answer(text=msg_final, reply_markup=kb)


@router.callback_query(F.data == 'change_vocab_name')
async def process_change_vocab_name(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Змінити назву словника" під час створення словника.
    Переводить стан FSM у очікування назви словника.
    """
    logging.info('Користувач натиснув на кнопку "Змінити назву словника" при його створенні')

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника

    msg_final: str = add_vocab_data_to_message(vocab_name=vocab_name, message=MSG_ENTER_NEW_VOCAB_NAME)

    # Клавіатура для створення назви словника з кнопкою "Залишити поточну назву"
    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name(is_keep_old_vocab_name=True)

    await save_current_fsm_state(state, VocabCreation.waiting_for_vocab_name)

    await callback.message.edit_text(text=msg_final, reply_markup=kb)


@router.callback_query(F.data == 'create_wordpairs_status')
async def process_create_wordpairs_status(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Статус" під час введення словникових пар"""
    logging.info('Користувач натиснув на кнопку "Статус" під час введення словникових пар')

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM

    vocab_name: str = data_fsm.get('vocab_name')
    vocab_description: str = data_fsm.get('vocab_description')
    validated_data_wordpairs: list | None = data_fsm.get('validated_data_wordpairs')  # Всі дані словникових пар

    # Клавіатура для створення словникових пар без кнопки "Статус"
    kb: InlineKeyboardMarkup = get_kb_create_wordpairs(is_keep_status=False)

    # Якщо немає доданих словникових пар
    if not validated_data_wordpairs:
        logging.info('Користувач не додав словникових пар')
        message_msg = f'Немає доданих словникових пар.\n\n{MSG_VOCAB_WORDPAIRS_SAVED_SMALL_INSTRUCTIONS}'
    else:
        formatted_wordpairs_lst: list = []

        for valid_data in validated_data_wordpairs:
            words_data_lst: list = valid_data['words']  # Список кортежів слів та їх анотацій
            translations_data_lst: list = valid_data['translations']  # Список кортежів перекладів та їх анотацій
            annotation: str = valid_data['annotation'] or '–'

            formatted_words: list[str] = ', '.join([f'{word} [{transcription or "–"}]' for
                                                    word, transcription in words_data_lst])
            formatted_translations: list[str] = ', '.join([f'{translation} [{transcription or "–"}]' for
                                                        translation, transcription in translations_data_lst])
            formatted_wordpair = f'{formatted_words} : {formatted_translations} : {annotation}'
            formatted_wordpairs_lst.append(formatted_wordpair)

        joined_wordpairs: str = '\n'.join([f'{num}. {i}' for num, i in enumerate(start=1,
                                                                                 iterable=formatted_wordpairs_lst)])

        message_msg: str = (
            f'Додані словникові пари:\n{joined_wordpairs}\n\n{MSG_VOCAB_WORDPAIRS_SAVED_SMALL_INSTRUCTIONS}')
    msg_final: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                            vocab_description=vocab_description,
                                            message=message_msg)

    await callback.message.edit_text(text=msg_final, reply_markup=kb)


@router.callback_query(F.data == 'save_vocab')
async def process_save_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Зберегти" під час введення словникових пар"""
    logging.info('Користувач натиснув на кнопку "Зберегти" під час введення словникових пар')

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM

    vocab_name: str = data_fsm.get('vocab_name')
    vocab_description: str = data_fsm.get('vocab_description')

    user_id: int = callback.from_user.id

    validated_data_wordpairs: Any | list = data_fsm.get('validated_data_wordpairs')  # Всі дані словникових пар

    # Якщо немає доданих словникових пар
    if not validated_data_wordpairs:
        logging.info('Користувач не додав словникових пар')

        message_msg = MSG_ERROR_NO_ADD_WORDPAIRS
        # Клавіатура для створення словникових пар без кнопки "Статус"
        kb: InlineKeyboardMarkup = get_kb_create_wordpairs(is_keep_status=False)
    else:
        await state.clear()  # Очищення FSM-кеш та FSM-стану
        logging.info('Очищення FSM стану')

        with Session() as db:
            add_vocab_to_db(db, user_id, vocab_name, vocab_description, validated_data_wordpairs)
        message_msg: str = MSG_SUCCESS_VOCAB_SAVED_TO_DB.format(vocab_name=vocab_name, menu=MSG_MENU)

        kb: InlineKeyboardMarkup = get_inline_kb_menu()

    msg_final: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                            vocab_description=vocab_description,
                                            message=message_msg)

    await callback.message.edit_text(text=msg_final, reply_markup=kb)


@router.callback_query(F.data == 'keep_old_vocab_name')
async def process_keep_old_vocab_name(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Залишити поточну назву" під час зміни назви словника.
    Залишає поточну назву та переводить стан FSM у очікування примітки до словника.
    """
    logging.info('Користувач натиснув на кнопку "Залишити поточну назву" '
                 'під час зміни назви словника')

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM
    kb: InlineKeyboardMarkup = get_kb_create_vocab_description()  # Клавіатура для примітки

    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника

    msg_final: str = add_vocab_data_to_message(vocab_name=vocab_name, message=MSG_ENTER_NEW_VOCAB_NAME)

    await save_current_fsm_state(state, VocabCreation.waiting_for_vocab_description)

    await callback.message.edit_text(text=msg_final, reply_markup=kb)


@router.callback_query(F.data == 'cancel_create_vocab')
async def process_cancel_create_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Скасувати" на всіх етапах створення словника.
    Залишає поточну назву та переводить стан FSM у очікування.
    """
    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM
    stage: str = data_fsm['current_stage']  # Процес, з якого було натиснута кнопка "Скасувати"

    logging.info(f'Була натиснута кнопка "Скасувати" при створенні словника, на етапі "{stage}"')

    await state.set_state()  # FSM у очікування

    logging.info('FSM стан переведено у очікування')

    kb: InlineKeyboardMarkup = get_kb_confirm_cancel()  # Клавіатура для підтвердження

    await callback.message.edit_text(text=MSG_CONFIRM_CANCEL_CREATE_VOCAB, reply_markup=kb)


@router.callback_query(F.data == 'cancel_no')
async def process_back_to_previous_stage(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Повертає користувача на попередній етап, з якого було натиснуто "Скасувати"."""
    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM
    previous_stage = data_fsm.get('current_stage')  # Отримуємо збережений попередній етап

    logging.info('Користувач натиснув на кнопку "Ні" для підтвердження скасування. '
                 f'Повернення на етап "{previous_stage}"')

    await state.set_state(previous_stage)
    logging.info(f'FSM стан змінено на "{previous_stage}"')

    vocab_name: str | None = data_fsm.get('vocab_name')
    vocab_description: str | None = data_fsm.get('vocab_description')

    if previous_stage == VocabCreation.waiting_for_vocab_name:
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()
        msg_text: str = add_vocab_data_to_message(vocab_name, vocab_description, MSG_ENTER_VOCAB_NAME)

    elif previous_stage == VocabCreation.waiting_for_vocab_description:
        kb: InlineKeyboardMarkup = get_kb_create_vocab_description()
        msg_text: str = add_vocab_data_to_message(vocab_name, vocab_description, MSG_ENTER_VOCAB_DESCRIPTION)

    elif previous_stage == VocabCreation.waiting_for_wordpairs:
        kb: InlineKeyboardMarkup = get_kb_create_wordpairs()
        msg_text: str = add_vocab_data_to_message(vocab_name, vocab_description, MSG_ENTER_WORDPAIRS)

    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.callback_query(F.data.startswith('skip_creation_note'))
async def process_skip_creation_note(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Пропустити" під час створення примітки до словника"""
    logging.info('Користувач натиснув на кнопку "Пропустити" під час створення примітки до словника')

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM

    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника
    vocab_description = DEFAULT_VOCAB_DESCRIPTION

    await state.update_data(vocab_description=vocab_description)  # Збереження примітки до словника в кеш FSM

    msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                            message=MSG_ENTER_WORDPAIRS)

    kb: InlineKeyboardMarkup = get_kb_create_wordpairs()  # Клавіатура для введення назви

    await save_current_fsm_state(state, VocabCreation.waiting_for_wordpairs)

    await callback.message.edit_text(text=msg_text, reply_markup=kb)
