from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.keyboards.help_kb import get_inline_kb_help

from db.database import Base, Session, engine
from db.models import WordPair, User, Dictionary

from tools.read_data import data

router = Router()


@router.callback_query(F.data == 'help')
async def process_btn_help(callback: CallbackQuery) -> None:
    with Session as db:
        text_help = data['prompt']['text_help']
        await callback.message.edit_text(text=text_help,
                                         reply_markup=get_inline_kb_help())
