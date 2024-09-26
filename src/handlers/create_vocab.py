
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from src.keyboards.create_vocab_kb import get_inline_kb_confirm_cancel, get_inline_kb_create_vocab

router = Router(name='create_vocab')


class VocabCreation(StatesGroup):
    waiting_for_vocab_name = State()  # Стан очікування назви словника


@router.callback_query(F.data == 'create_vocab')
async def process_add_vocab(callback: CallbackQuery, state: FSMContext) -> None:
    """Відстежує натискання на кнопку "Додати новий словник".
    Виконується процес створення словника.
    """
    kb: InlineKeyboardMarkup = get_inline_kb_create_vocab()
    await callback.message.edit_text(text='Введіть назву словника:', reply_markup=kb)

    # Перевод FSM у стан очікування назви
    await state.set_state(VocabCreation.waiting_for_vocab_name)


@router.message(VocabCreation.waiting_for_vocab_name)
async def process_vocab_name(message: Message, state: FSMContext) -> None:
    """Обробляє назву словника, яку ввів користувач"""
    vocab_name: str | None = message.text  # Назва словника, введена користувачем

    # Тут можна додати логіку для збереження назви в БД або переходу до наступного етапу
    await message.answer(f'Ви ввели назву словника: {vocab_name}')

    # Після цього можна завершити стан або перейти до наступного етапу
    await state.clear()  # Завершуємо процес


@router.callback_query(F.data == 'cancel_create_vocab')
async def process_confirm_cancel(callback: CallbackQuery) -> None:
    """Відстежує натискання на кнопку "Скасувати".
    Відправляється кнопки з підтвердженням скасування.
    """
    kb: InlineKeyboardMarkup = get_inline_kb_confirm_cancel()

    await callback.message.edit_text(text='Ви дійсно хочете скасувати створення словника?', reply_markup=kb)
