from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.keyboards.help_kb import get_inline_kb_help
from db.database import Base, Session, engine
from db.models import WordPair, User, Dictionary

from datetime import date

router = Router()


@router.callback_query(F.data == 'help')
async def process_btn_help(callback: CallbackQuery) -> None:
    with Session as db:
        text_help = 'Допомога'
        # db.add_all([
        #     User(user_id=5950587277, username='pyquent',
        #          first_name='ads', last_name='gg'),
        #     Dictionary(dictionary_name='Dict1',
        #                created_date=date.today(), user_id=1, note='note1'),
        #     Dictionary(dictionary_name='Dict2', wordpair_count=2,
        #                created_date=date.today(), user_id=1, note='note2'),
        #     Wordpair(word_1='w_1', annotation_1='a_1',
        #              word_2='w_2', annotation_2='a_2', dictionary_id=1),
        #     Wordpair(word_1='w_3', annotation_1='a_3',
        #              word_2='w_4', annotation_2='a_4', dictionary_id=1),
        #     Wordpair(word_1='w_5', annotation_1='a_5',
        #              word_2='w_6', annotation_2='a_6',  # ID словаря, который тренировали
        #              dictionary_id=1),
        #     Wordpair(word_1='w_11', annotation_1='a_11',
        #              word_2='w_22', annotation_2='a_22', dictionary_id=2),
        #     Wordpair(word_1='w_33', annotation_1='a_33',
        #              word_2='w_44', annotation_2='a_44', dictionary_id=2),
        #     Wordpair(word_1='w_55', annotation_1='a_55',
        #              word_2='w_66', annotation_2='a_66',  # ID словаря, который тренировали
        #              dictionary_id=1),
        # ])
        # db.commit()
        await callback.message.edit_text(text=text_help,
                                         reply_markup=get_inline_kb_help())
