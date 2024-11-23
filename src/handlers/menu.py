import logging

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.user import User

from db.crud import UserCRUD
from db.database import Session
from src.keyboards.menu_kb import get_kb_menu
from text_data import MSG_TITLE_MENU, MSG_TITLE_MENU_FOR_NEW_USER

router = Router(name='menu')
logger: logging.Logger = logging.getLogger(__name__)


@router.message(Command(commands=['start', 'menu']))
async def cmd_menu(message: types.Message) -> None:
    """Відстежує введення команди "help" та "menu".
    Перенаправляє до розділу "Головне меню".
    """
    user_id: int = message.from_user.id

    logger.info(f'Користувач ввів команду "{message.text}"')
    logger.info(f'Користувач перейшов до розділу "Головне меню". USER_ID: {user_id}')

    tg_user_data: User = message.from_user

    kb: InlineKeyboardMarkup = get_kb_menu()

    with Session() as session:
        user_crud = UserCRUD(session)
        user_id: int = tg_user_data.id

        if user_crud.check_user_exists_in_db(user_id):
            msg_title_menu: str = MSG_TITLE_MENU
        else:
            msg_title_menu: str = MSG_TITLE_MENU_FOR_NEW_USER
            user_crud.create_new_user(tg_user_data)
            logger.info(f'До БД був доданий користувач. USER_ID: {user_id}')
    await message.answer(text=msg_title_menu, reply_markup=kb)


@router.callback_query(F.data == 'menu')
async def process_btn_menu(callback: types.CallbackQuery) -> None:
    """Відстежує натискання на кнопку "Головне меню".
    Перенаправляє до розділу "Головне меню".
    """
    user_id: int = callback.from_user.id

    logger.info(f'Користувач перейшов до розділу "Головне меню". USER_ID: {user_id}')

    kb: InlineKeyboardMarkup = get_kb_menu()
    msg_title_menu: str = MSG_TITLE_MENU

    await callback.message.edit_text(text=msg_title_menu, reply_markup=kb)
