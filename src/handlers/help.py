from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from src.keyboards.help_kb import get_inline_kb_help
from tools.read_data import app_data

router = Router()


@router.callback_query(F.data == 'help')
async def process_btn_help(callback: CallbackQuery) -> None:
    """Відстежує натискання на кнопку допомоги".
    Відправляє користувачу повідомлення з допомогою.
    """
    title_help: str = app_data['handlers']['help']['title_help']
    kb: InlineKeyboardMarkup = get_inline_kb_help()

    await callback.message.edit_text(text=title_help,
                                     reply_markup=kb,
                                     parse_mode=ParseMode.HTML)
