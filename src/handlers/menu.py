import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from db import crud
from db.database import Session
from db.models import User
from src.keyboards.menu_kb import get_inline_kb_menu
from text_data import MSG_TITLE_MENU, MSG_TITLE_MENU_FOR_NEW_USER

router = Router(name='menu')
logger: logging.Logger = logging.getLogger(__name__)


@router.message(Command(commands=['start', 'menu']))
async def cmd_menu(message: Message) -> None:
    logging.info(f'Користувач ввів команду "{message.text}" для переходу до "Головного меню"')

    tg_user_data: User | None = message.from_user

    kb: InlineKeyboardMarkup = get_inline_kb_menu()

    try:
        with Session() as session:
            user_crud = crud.UserCRUD(session=session)
            user_id: int = tg_user_data.id

            if user_crud.check_user_exists_in_db(user_id):
                msg_text: str = MSG_TITLE_MENU
            else:
                msg_text: str = MSG_TITLE_MENU_FOR_NEW_USER
                user_crud.add_new_user_to_db(tg_user_data)
                logger.info(f'ДО БД був доданий користувач: {user_id}')
    except Exception as e:
        logger.error(e)
        return

    await message.answer(text=msg_text, reply_markup=kb)


@router.callback_query(F.data == 'menu')
async def process_btn_menu(callback: CallbackQuery) -> None:
    logging.info('Користувач натиснув на кнопку для переходу до "Головного меню"')

    kb: InlineKeyboardMarkup = get_inline_kb_menu()
    msg_text: str = MSG_TITLE_MENU

    await callback.message.edit_text(text=msg_text, reply_markup=kb)
