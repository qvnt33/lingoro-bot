import logging
from typing import Any, Dict

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from db.crud import add_vocab_to_db
from db.database import Session
from src.fsm.states import VocabCreation
from src.keyboards.create_vocab_kb import (
    get_inline_kb_confirm_cancel,
    get_inline_kb_create_vocab_description,
    get_inline_kb_create_vocab_name,
    get_inline_kb_create_wordpairs,
)
from src.keyboards.menu_kb import get_inline_kb_menu
from src.validators.vocab.vocab_description_validator import VocabDescriptionValidator
from src.validators.vocab.vocab_name_validator import VocabNameValidator
from src.validators.wordpair.wordpair_validator import WordpairValidator
from text_data import (
    MSG_CONFIRM_CANCEL_CREATE_VOCAB,
    MSG_ENTER_NEW_VOCAB_NAME,
    MSG_ENTER_VOCAB_DESCRIPTION,
    MSG_ENTER_VOCAB_NAME,
    MSG_ENTER_WORDPAIRS,
    MSG_ERROR_VOCAB_DESCRIPTION_INVALID,
    MSG_ERROR_VOCAB_NAME_DUPLICATE,
    MSG_ERROR_VOCAB_NAME_INVALID,
    MSG_ERROR_WORDPAIRS_NO_ADDED,
    MSG_ERROR_WORDPAIRS_NO_VALID,
    MSG_INFO_ADDED_WORDPAIRS,
    MSG_INFO_NO_ADDED_WORDPAIRS,
    MSG_SUCCESS_ALL_WORDPAIRS_VALID,
    MSG_SUCCESS_VOCAB_SAVED_TO_DB,
    MSG_TITLE_MENU,
)
from tools.message_formatter import add_vocab_data_to_message

logger: logging.Logger = logging.getLogger(__name__)
router = Router(name='create_vocab')


async def save_current_fsm_state(state: FSMContext, new_state: State) -> None:
    """Зберігає поточний стан FSM та оновлює FSM-Cache зі значенням нового стану"""
    await state.set_state(new_state)
    logger.info(f'FSM стан змінено на "{new_state}"')

    await state.update_data(current_stage=new_state)
    logger.info(f'FSM стан "{new_state}" збережений у FSM-Cache, як поточний стан')


def check_vocab_name_duplicate(vocab_name: str, vocab_name_old: str) -> bool:
    """Перевіряє, чи збігається нова назва словника з поточною"""
    return vocab_name_old is not None and vocab_name.lower() == vocab_name_old.lower()


@router.callback_query(F.data == 'create_vocab')
async def process_create_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    logger.info(f'[START] Створення словника. USER_ID: {callback.from_user.id}')

    await state.clear()
    logger.info('FSM стан та FSM-Cache очищено')

    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()
    msg_text: str = add_vocab_data_to_message(message_text=MSG_ENTER_VOCAB_NAME)

    await save_current_fsm_state(state, new_state=VocabCreation.waiting_for_vocab_name)

    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.message(VocabCreation.waiting_for_vocab_name)
async def process_create_vocab_name(message: types.Message, state: FSMContext) -> None:
    """Обробляє назву словника, яку ввів користувач"""
    data_fsm: Dict[str, Any] = await state.get_data()

    vocab_name: str = message.text.strip()
    vocab_name_old: str | None = data_fsm.get('vocab_name')  # Поточна назва словника (якщо є)

    logger.info(f'Користувач ввів назву словника: {vocab_name}')

    if check_vocab_name_duplicate(vocab_name, vocab_name_old):
        logger.warning('Назва словника збігається з поточною')
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name(is_keep_old_vocab_name=True)
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                  message_text=MSG_ERROR_VOCAB_NAME_DUPLICATE)
        await message.answer(text=msg_text, reply_markup=kb)
        return  # Завершення обробки, якщо назва збігається

    with Session() as session:
        validator_vocab_name = VocabNameValidator(name=vocab_name,
                                                  user_id=message.from_user.id,
                                                  db_session=session)

    if validator_vocab_name.is_valid():
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_description()
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                  message_text=MSG_ENTER_VOCAB_DESCRIPTION)

        await state.update_data(vocab_name=vocab_name)
        logger.info('Назва словника збережена у FSM-Cache')

        await save_current_fsm_state(state, new_state=VocabCreation.waiting_for_vocab_description)
    else:
        formatted_errors: str = validator_vocab_name.format_errors()

        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name_old,
                                                  message_text=MSG_ERROR_VOCAB_NAME_INVALID.format(
                                                      vocab_name=vocab_name,
                                                      errors=formatted_errors))
    await message.answer(text=msg_text, reply_markup=kb)


@router.callback_query(F.data == 'skip_create_vocab_description')
async def process_skip_create_vocab_description(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Пропустити" під час створення примітки до словника"""
    logger.info('Користувач натиснув на кнопку "Пропустити" під час створення примітки до словника')

    data_fsm: Dict[str, Any] = await state.get_data()
    vocab_name: str | None = data_fsm.get('vocab_name')

    kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs()
    msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                              message_text=MSG_ENTER_WORDPAIRS)

    await save_current_fsm_state(state, new_state=VocabCreation.waiting_for_wordpairs)
    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.message(VocabCreation.waiting_for_vocab_description)
async def process_create_vocab_description(message: types.Message, state: FSMContext) -> None:
    """Обробляє опис словника, який ввів користувач"""
    data_fsm: dict = await state.get_data()

    vocab_name: str | None = data_fsm.get('vocab_name')
    vocab_description: str = message.text.strip()

    logger.info(f'Користувач ввів опис словника: {vocab_description}')

    kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs()

    validator_description = VocabDescriptionValidator(description=vocab_description)
    if validator_description.is_valid():
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                  vocab_description=vocab_description,
                                                  message_text=MSG_ENTER_WORDPAIRS)

        await state.update_data(vocab_description=vocab_description)
        logger.info('Опис словника збережений у FSM-Cache')

        await save_current_fsm_state(state, new_state=VocabCreation.waiting_for_wordpairs)
    else:
        formatted_errors: str = validator_description.format_errors()
        msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                                  message_text=MSG_ERROR_VOCAB_DESCRIPTION_INVALID.format(
                                                      description=vocab_description,
                                                      vocab_name=vocab_name,
                                                      errors=formatted_errors))
    await message.answer(text=msg_text, reply_markup=kb)


@router.message(VocabCreation.waiting_for_wordpairs)
async def process_create_wordpairs(message: types.Message, state: FSMContext) -> None:
    """Обробляє словникові пари, введені користувачем"""
    data_fsm: Dict[str, Any] = await state.get_data()

    vocab_name: str | None = data_fsm.get('vocab_name')
    vocab_description: str | None = data_fsm.get('vocab_description')

    wordpairs: str = message.text.strip()
    logger.info(f'Користувач ввів словникові пари: {wordpairs}')

    valid_wordpairs, invalid_wordpairs = [], []  # ?

    validated_data_wordpairs: Any | list = data_fsm.get('validated_data_wordpairs') or []  # ? Всі дані словникових пар

    kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs()

    for wordpair in wordpairs.split('\n'):
        validator_wordpair = WordpairValidator(wordpair)

        if validator_wordpair.is_valid():
            logger.info(f'Словникова пара "{wordpair}" ВАЛІДНА')

            valid_wordpairs.append(wordpair)

            validated_data: dict = validator_wordpair.validated_data  # Словник з даними словникової пари
            validated_data_wordpairs.append(validated_data)
        else:
            logger.warning(f'Словникова пара "{wordpair}" НЕ ВАЛІДНА')

            formatted_errors: str = validator_wordpair.format_errors()
            invalid_wordpairs.append({
                'wordpair': wordpair,
                'errors': formatted_errors})

    # Якщо є валідні словникові пар
    if valid_wordpairs:
        joined_valid_wordpairs: str = '\n'.join([f'- {wordpair}' for wordpair in valid_wordpairs])
        valid_msg: str = MSG_INFO_ADDED_WORDPAIRS.format(wordpairs=joined_valid_wordpairs)
    else:
        valid_msg = MSG_ERROR_WORDPAIRS_NO_VALID

    # Збереження всіх даних словникових пар в FSM-кеш
    await state.update_data(validated_data_wordpairs=validated_data_wordpairs)

    # Якщо є не валідні словникові пар
    if invalid_wordpairs:
        invalid_msg_parts_lst: list = []
        for wordpair in invalid_wordpairs:
            # Кожна словникова пара та помилки
            sep_invalid_wordpair: str = f'- {wordpair["wordpair"]}\n{wordpair["errors"]}'
            invalid_msg_parts_lst.append(sep_invalid_wordpair)

        joined_invalid_wordpairs: str = '\n'.join(invalid_msg_parts_lst)
        invalid_msg: str = MSG_INFO_NO_ADDED_WORDPAIRS.format(wordpairs=joined_invalid_wordpairs)
    else:
        invalid_msg: str = MSG_SUCCESS_ALL_WORDPAIRS_VALID

    msg_message = 'MSG_VOCAB_WORDPAIRS_SAVED_SMALL_INSTRUCTIONS'
    msg_for_status: str = '\n\n'.join((valid_msg, invalid_msg, msg_message))

    msg_final: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                            vocab_description=vocab_description,
                                            message_text=msg_for_status)

    await message.answer(text=msg_final, reply_markup=kb)


@router.callback_query(F.data == 'change_vocab_name')
async def process_change_vocab_name(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Змінити назву словника" під час створення словника.
    Переводить стан FSM у очікування назви словника.
    """
    logger.info('Користувач натиснув на кнопку "Змінити назву словника" при його створенні')

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM
    vocab_name: Any | None = data_fsm.get('vocab_name')  # Назва словника

    msg_final: str = add_vocab_data_to_message(vocab_name=vocab_name, message_text=MSG_ENTER_NEW_VOCAB_NAME)

    # Клавіатура для створення назви словника з кнопкою "Залишити поточну назву"
    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name(is_keep_old_vocab_name=True)

    await save_current_fsm_state(state, VocabCreation.waiting_for_vocab_name)  # Зберегти та оновити FSM стан

    await callback.message.edit_text(text=msg_final, reply_markup=kb)


@router.callback_query(F.data == 'create_wordpairs_status')
async def process_create_wordpairs_status(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Статус" під час введення словникових пар"""
    logger.info('Користувач натиснув на кнопку "Статус" під час введення словникових пар')

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM

    vocab_name: str = data_fsm.get('vocab_name')
    vocab_description: str = data_fsm.get('vocab_description')
    validated_data_wordpairs: list | None = data_fsm.get('validated_data_wordpairs')  # Всі дані словникових пар

    # Клавіатура для створення словникових пар без кнопки "Статус"
    kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs(is_keep_status=False)

    # Якщо немає доданих словникових пар
    if not validated_data_wordpairs:
        logger.info('Користувач не додав словникових пар')
        message_msg = f'Немає доданих словникових пар.\n\n{'MSG_VOCAB_WORDPAIRS_SAVED_SMALL_INSTRUCTIONS'}'
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
            f'Додані словникові пари:\n{joined_wordpairs}\n\n{'MSG_VOCAB_WORDPAIRS_SAVED_SMALL_INSTRUCTIONS'}')
    msg_final: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                            vocab_description=vocab_description,
                                            message_text=message_msg)

    await callback.message.edit_text(text=msg_final, reply_markup=kb)


@router.callback_query(F.data == 'save_vocab')
async def process_save_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Зберегти" під час введення словникових пар"""
    logger.info('Користувач натиснув на кнопку "Зберегти" під час введення словникових пар')

    data_fsm: Dict[str, Any] = await state.get_data()  # Дані з FSM

    vocab_name: str = data_fsm.get('vocab_name')
    vocab_description: str = data_fsm.get('vocab_description')

    user_id: int = callback.from_user.id

    validated_data_wordpairs: Any | list = data_fsm.get('validated_data_wordpairs')  # Всі дані словникових пар

    # Якщо немає доданих словникових пар
    if not validated_data_wordpairs:
        logger.info('Користувач не додав словникових пар')

        message_msg = MSG_ERROR_WORDPAIRS_NO_ADDED
        # Клавіатура для створення словникових пар без кнопки "Статус"
        kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs(is_keep_status=False)
    else:
        await state.clear()  # Очищення FSM-кеш та FSM-стану
        logger.info('Очищення FSM стану')

        with Session() as db:
            add_vocab_to_db(db, user_id, vocab_name, vocab_description, validated_data_wordpairs)
        message_msg: str = MSG_SUCCESS_VOCAB_SAVED_TO_DB.format(vocab_name=vocab_name, menu=MSG_TITLE_MENU)

        kb: InlineKeyboardMarkup = get_inline_kb_menu()

    msg_final: str = add_vocab_data_to_message(vocab_name=vocab_name,
                                            vocab_description=vocab_description,
                                            message_text=message_msg)

    await callback.message.edit_text(text=msg_final, reply_markup=kb)


@router.callback_query(F.data == 'keep_old_vocab_name')
async def process_keep_old_vocab_name(callback: types.CallbackQuery, state: FSMContext) -> None:
    logger.info('Користувач натиснув на кнопку "Залишити поточну назву" під час зміни назви словника')

    data_fsm: Dict[str, Any] = await state.get_data()
    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_description()

    vocab_name: str | None = data_fsm.get('vocab_name')

    msg_text: str = add_vocab_data_to_message(vocab_name=vocab_name, message_text=MSG_ENTER_VOCAB_NAME)

    await save_current_fsm_state(state, new_state=VocabCreation.waiting_for_vocab_description)

    await callback.message.edit_text(text=msg_text, reply_markup=kb)


@router.callback_query(F.data == 'cancel_create_vocab')
async def process_cancel_create_vocab(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Скасувати" при створенні словника.
    Відправляє клавіатуру для підтвердження скасування.
    """
    data_fsm: Dict[str, Any] = await state.get_data()
    current_stage: Any | None = data_fsm.get('current_stage')
    logger.info(f'Була натиснута кнопка "Скасувати" при створенні словника, на етапі "{current_stage}"')

    await state.set_state()
    logger.info('FSM стан переведено у очікування')

    kb: InlineKeyboardMarkup = get_inline_kb_confirm_cancel()

    await callback.message.edit_text(text=MSG_CONFIRM_CANCEL_CREATE_VOCAB, reply_markup=kb)


@router.callback_query(F.data == 'cancel_no')
async def process_back_to_previous_stage(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Ні" при скасуванні створення словника.
    Повертає користувача до попереднього етапу (на якому була натиснута кнопка "Скасувати").
    """
    data_fsm: Dict[str, Any] = await state.get_data()
    previous_stage: Any | None = data_fsm.get('current_stage')

    logger.info('Користувач натиснув на кнопку "Ні" під час підтвердження скасування створення словника')
    logger.info('Повернення на етап "{previous_stage}"')

    await state.set_state(previous_stage)
    logger.info(f'FSM стан змінено на "{previous_stage}"')

    vocab_name: str | None = data_fsm.get('vocab_name')
    vocab_description: str | None = data_fsm.get('vocab_description')

    if previous_stage == VocabCreation.waiting_for_vocab_name:
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_name()
        msg_text: str = add_vocab_data_to_message(vocab_name, vocab_description, MSG_ENTER_VOCAB_NAME)

    elif previous_stage == VocabCreation.waiting_for_vocab_description:
        kb: InlineKeyboardMarkup = get_inline_kb_create_vocab_description()
        msg_text: str = add_vocab_data_to_message(vocab_name, vocab_description, MSG_ENTER_VOCAB_DESCRIPTION)

    elif previous_stage == VocabCreation.waiting_for_wordpairs:
        kb: InlineKeyboardMarkup = get_inline_kb_create_wordpairs()
        msg_text: str = add_vocab_data_to_message(vocab_name, vocab_description, MSG_ENTER_WORDPAIRS)

    await callback.message.edit_text(text=msg_text, reply_markup=kb)
