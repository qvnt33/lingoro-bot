from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from src.keyboards.help_kb import get_inline_kb_help

from tools.read_data import data

router = Router()


@router.callback_query(F.data == 'help')
async def process_btn_help(callback: CallbackQuery) -> None:
    text_help: str = data['prompt']['text_help']
    kb: InlineKeyboardMarkup = get_inline_kb_help()

    await callback.message.edit_text(text=text_help,
                                     reply_markup=kb)
