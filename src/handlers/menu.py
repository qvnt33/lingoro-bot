from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.enums import ParseMode

from src.keyboards.menu_kb import get_inline_kb_menu
from tools.read_data import app_data

router = Router()


@router.message(Command(commands=['start', 'menu']))
async def cmd_menu(message: Message) -> None:
    """Переходить у головне меню після введення команд"""
    kb: InlineKeyboardMarkup = get_inline_kb_menu()

    await message.answer(
        text=app_data['handlers']['menu']['title_menu'],
        reply_markup=kb,
        parse_mode=ParseMode.HTML)


@router.callback_query(F.data == 'menu')
async def process_back_to_menu(callback: CallbackQuery) -> None:
    """Переходить у головне меню після натискання на кнопку"""
    kb: InlineKeyboardMarkup = get_inline_kb_menu()

    await callback.message.edit_text(
        text=app_data['handlers']['menu']['title_menu'],
        reply_markup=kb,
        parse_mode=ParseMode.HTML)
