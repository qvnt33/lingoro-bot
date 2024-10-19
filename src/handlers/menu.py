import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from db.database import Session
from db.models import User
from db.crud import create_user

from messages import MSG_MENU, MSG_MENU_FOR_NEW_USER
from src.keyboards.menu_kb import get_inline_kb_menu

router = Router(name='menu')


@router.callback_query(F.data == 'neutral_call')
async def process_neutral_call(callback: CallbackQuery) -> None:
    """Заглушка для callback"""
    # Відповідаємо на callback-запит без відправлення повідомлення
    await callback.answer()


@router.message(Command(commands=['start', 'menu']))
async def cmd_menu(message: Message) -> None:
    """Відстежує введення команд "start, menu".
    Відправляє користувачу повідомлення головного меню.
    """
    logging.info('Користувач ввів команду "start, menu" для переходу до головного меню')

    telegram_user: User | None = message.from_user

    kb: InlineKeyboardMarkup = get_inline_kb_menu()

    with Session() as db:
        # Чи є користувач у БД
        is_user_exists: bool = db.query(User).filter(User.user_id == telegram_user.id).first() is not None

        if is_user_exists:
            title_menu: str = MSG_MENU
        else:
            title_menu: str = MSG_MENU_FOR_NEW_USER
            # Додавання користувача до БД
            create_user(db, telegram_user)
            db.commit()

    await message.answer(text=title_menu, reply_markup=kb)


@router.callback_query(F.data == 'menu')
async def process_btn_back_to_menu(callback: CallbackQuery) -> None:
    """Відстежує натискання на кнопку "меню".
    Відправляє користувачу повідомлення головного меню.
    """
    logging.info('Користувач натиснув кнопку для переходу до головного меню')

    tg_user: User | None = callback.from_user

    kb: InlineKeyboardMarkup = get_inline_kb_menu()

    with Session() as db:
        # Чи є користувач у БД
        is_user_exists: bool = db.query(User).filter(User.user_id == tg_user.id).first() is not None

        if is_user_exists:
            title_menu: str = MSG_MENU
        else:
            title_menu: str = MSG_MENU_FOR_NEW_USER
            # Додавання користувача до БД
            user = User(user_id=tg_user.id,
                        username=tg_user.username,
                        first_name=tg_user.first_name,
                        last_name=tg_user.last_name)
            db.add(user)

            logging.info(f'Був доданий до БД користувач: {tg_user.id}')

            db.commit()

    await callback.message.answer(text=title_menu, reply_markup=kb)
