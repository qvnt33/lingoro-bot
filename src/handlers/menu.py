import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from db import crud
from db.database import Session
from db.models import User
from src.keyboards.menu_kb import get_inline_kb_menu
from text_data import MSG_MENU, MSG_MENU_FOR_NEW_USER

router = Router(name='menu')


@router.message(Command(commands=['start', 'menu']))
async def cmd_menu(message: Message) -> None:
    logging.info(f'Користувач ввів команду "/{message.text}" для переходу до "Головного меню"')

    tg_user_data: User | None = message.from_user

    kb: InlineKeyboardMarkup = get_inline_kb_menu()

    with Session() as db:
        if crud.is_user_exists_in_db(db=db, user_id=tg_user_data.id):
            title_menu: str = MSG_MENU
        else:
            title_menu: str = MSG_MENU_FOR_NEW_USER
            crud.create_user_in_db(db, tg_user_data)
            logging.info(f'ДО БД був доданий користувач: {tg_user_data.id}')
            db.commit()

    await message.answer(text=title_menu, reply_markup=kb)


@router.callback_query(F.data == 'menu')
async def process_btn_menu(callback: CallbackQuery) -> None:
    logging.info('Користувач натиснув на кнопку для переходу до "Головного меню"')

    tg_user_data: User | None = callback.from_user

    kb: InlineKeyboardMarkup = get_inline_kb_menu()

    with Session() as db:
        if crud.is_user_exists_in_db(db, user_id=tg_user_data.id):
            title_menu: str = MSG_MENU
        else:
            title_menu: str = MSG_MENU_FOR_NEW_USER
            crud.create_user_in_db(db, tg_user_data)
            logging.info(f'ДО БД був доданий користувач: {tg_user_data.id}')
            db.commit()

    await callback.message.edit_text(text=title_menu, reply_markup=kb)
