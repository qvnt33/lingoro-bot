from typing import Any

import sqlalchemy
from .callback_data import PaginationCallback
from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from sqlalchemy import Column
from sqlalchemy.orm.query import Query

from db.database import Session
from db.models import Translation, Vocabulary, Word, WordPair, WordPairTranslation, WordPairWord
from src.keyboards.vocab_base_kb import get_inline_kb_vocab_base, get_inline_kb_add_vocab
from tools.read_data import app_data

router = Router(name='vocab_base')


@router.callback_query(PaginationCallback.filter(F.name == 'vocab_base'))
async def process_vocab_base(callback: CallbackQuery, callback_data: PaginationCallback) -> None:
    """Відстежує натискання на кнопку "База словників".
    Відправляє користувачу словники у вигляді кнопок.
    """
    user_id: int = callback.from_user.id

    current_page: int = callback_data.page  # Поточна сторінка
    limit: int = callback_data.limit  # Ліміт словників на сторінці

    vocab_lst: list = []  # Список всіх словників

    with Session() as db:
        # Отримання всіх словників користувача
        user_vocabs: Query[Vocabulary] = db.query(Vocabulary).filter(Vocabulary.user_id == user_id)

        # Перевірка, чи порожня база словників
        is_vocab_base_empty: bool = user_vocabs.first() is None

        # Якщо база порожня, повідомлення для порожньої бази
        if is_vocab_base_empty:
            msg_vocab_base: str = app_data['handlers']['vocab_base']['vocab_base_is_empty']
        else:
            msg_vocab_base: str = app_data['handlers']['vocab_base']['msg_select_vocab']

        for vocab in user_vocabs:
            vocab_id: Column[int] = vocab.id

            vocab_dict: dict = get_vocabulary_dict(vocab_id, db)  # Словник (dict) із словниковими парами
            vocab_lst.append(vocab_dict)  # Додавання до списку словників словник (dict)

    total_vocabs: int = user_vocabs.count()  # Кількість всіх словників
    total_pages_pagination: int = (total_vocabs + limit - 1) // limit  # Кількість всіх можливих сторінок пагінації

    # Перевірка меж сторінок
    if current_page <= 0:
        current_page = total_pages_pagination  # Присвоєння першої сторінки на останню
    elif current_page > total_pages_pagination:
        current_page = 1  # Присвоєння останньої сторінки на першу

    start_offset: int = (current_page - 1) * limit  # Початковий індекс для відображення словників
    end_offset: int = min(start_offset + limit, total_vocabs)  # Кінцевий індекс для відображення словників

    # Клавіатура для відображення словників із пагінацією
    kb: InlineKeyboardMarkup = get_inline_kb_vocab_base(vocab_lst,
                                                        start_offset,
                                                        end_offset,
                                                        current_page,
                                                        total_pages_pagination,
                                                        limit,
                                                        is_vocab_base_empty)

    await callback.message.edit_text(text=msg_vocab_base, reply_markup=kb)


def get_vocabulary_dict(vocab_id: int, db: sqlalchemy.orm.session.Session) -> dict:
    """Повертає згенерований словник (dict) для одного словника з словниковими парами"""
    vocab: Query[Vocabulary] | None = db.query(Vocabulary).filter(Vocabulary.id == vocab_id).first()

    # Перевірка, чи існує словник
    if not vocab:
        return {}

    # Структура для зберігання даних словника
    vocab_dict: dict[str, Any] = {
        'id': vocab.id,
        'name': vocab.name,
        'wordpairs': []}

    # Всі словникові пари словника
    wordpairs: list = db.query(WordPair).filter(WordPair.vocabulary_id == vocab.id).all()

    for pair in wordpairs:
        # Слова всіх словникових пар словника
        words: list[tuple] | list = db.query(Word.word).join(
            WordPairWord, Word.id == WordPairWord.word_id).filter(
                WordPairWord.wordpair_id == pair.id).all()

        # Переклади всіх словникових пар словника
        translations: list[tuple] | list = db.query(Translation.translation).join(
            WordPairTranslation, Translation.id == WordPairTranslation.translation_id).filter(
                WordPairTranslation.wordpair_id == pair.id).all()

        # Структура пари слів
        wordpair_dict: dict[str[tuple | None]] = {
            'word': words[0] if words else None,  # Якщо немає слова, то None
            'translation': translations[0] if translations else None,  # Якщо немає перекладу, то None
        }

        # Додавання анотації, якщо вона є
        if pair.annotation:
            wordpair_dict['annotation'] = pair.annotation

        # Додавання словникову пару до списку wordpairs у словнику (dict)
        vocab_dict['wordpairs'].append(wordpair_dict)

    return vocab_dict
