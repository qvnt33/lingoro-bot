from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from src.keyboards.menu_kb import get_inline_kb_menu
from tools.read_data import app_data

router = Router()


@router.message(Command(commands=['start', 'menu']))
async def cmd_menu(message: Message) -> None:
    """Відстежує введення команди "start, menu".
    Відправляє користувачу повідомлення головного меню.
    """
    title_menu: str = app_data['handlers']['menu']['title_menu']
    kb: InlineKeyboardMarkup = get_inline_kb_menu()

    await message.answer(
        text=title_menu,
        reply_markup=kb)


@router.callback_query(F.data == 'menu')
async def process_btn_back_to_menu(callback: CallbackQuery) -> None:
    """Відстежує натискання на кнопку меню".
    Відправляє користувачу повідомлення головного меню.
    """
    title_menu: str = app_data['handlers']['menu']['title_menu']
    kb: InlineKeyboardMarkup = get_inline_kb_menu()

    await callback.message.edit_text(
        text=title_menu,
        reply_markup=kb)
