from aiogram import F, Router, types
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from src.keyboards.help_kb import get_inline_kb_help
from text_data import MSG_TITLE_HELP

router = Router()


@router.callback_query(F.data == 'help')
async def process_btn_help(callback: types.CallbackQuery) -> None:
    """Відстежує натискання на кнопку "Довідка" у головному меню.
    Відправляє повідомлення з інструкціями.
    """
    kb: InlineKeyboardMarkup = get_inline_kb_help()
    msg_text: str = MSG_TITLE_HELP

    await callback.message.edit_text(text=msg_text, reply_markup=kb)
