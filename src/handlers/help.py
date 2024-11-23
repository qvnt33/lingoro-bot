import logging

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from src.keyboards.help_kb import get_kb_help
from text_data import MSG_TITLE_HELP

router = Router(name='help')
logger: logging.Logger = logging.getLogger(__name__)


@router.message(Command(commands=['help']))
async def cmd_menu(message: types.Message) -> None:
    """Відстежує введення команди "help".
    Перенаправляє до розділу "Довідка".
    """
    user_id: int = message.from_user.id

    logger.info(f'Користувач ввів команду "{message.text}"')
    logger.info(f'Користувач перейшов до розділу "Довідка". USER_ID: {user_id}')

    kb: InlineKeyboardMarkup = get_kb_help()
    msg_help_info: str = MSG_TITLE_HELP

    await message.answer(text=msg_help_info, reply_markup=kb)


@router.callback_query(F.data == 'help')
async def process_btn_help(callback: types.CallbackQuery) -> None:
    """Відстежує натискання на кнопку "Довідка" у головному меню.
    Відправляє повідомлення з інструкціями.
    """
    user_id: int = callback.from_user.id

    logger.info(f'Користувач перейшов до розділу "Довідка". USER_ID: {user_id}')

    kb: InlineKeyboardMarkup = get_kb_help()
    msg_help_info: str = MSG_TITLE_HELP

    await callback.message.edit_text(text=msg_help_info, reply_markup=kb)
