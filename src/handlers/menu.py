from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.enums import ParseMode

from src.keyboards.menu_kb import get_inline_kb_menu
from tools.read_data import data

router = Router()


@router.message(Command(commands=['start', 'menu']))
async def cmd_menu(message: Message):
    """Переходим в главное меню после ввода команд"""
    await message.answer(
        text=data['prompt']['text_menu'],
        reply_markup=get_inline_kb_menu(),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data == 'menu')
async def process_back_to_menu(callback: CallbackQuery):
    """Переходим в главное меню после нажатия кнопки"""
    await callback.message.edit_text(
        text=data['prompt']['text_menu'],
        reply_markup=get_inline_kb_menu(),
        parse_mode=ParseMode.HTML
    )
