from typing import Any

import sqlalchemy
from .callback_data import PaginationCallback
from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from sqlalchemy import Column
from sqlalchemy.orm.query import Query

from db.crud import get_user_vocabs_by_user_id, get_user_vocabs_by_vocab_id
from db.database import Session
from db.models import Translation, Vocabulary, Word, WordPair, WordPairTranslation, WordPairWord
from src.keyboards.vocab_base_kb import get_inline_kb_vocab_base
from text_data import MSG_ENTER_VOCAB, MSG_ERROR_VOCAB_BASE_EMPTY

router = Router(name='vocab_base')


@router.callback_query(PaginationCallback.filter(F.name == 'vocab_base'))
async def process_vocab_base(callback: CallbackQuery, callback_data: PaginationCallback) -> None:
    """Відстежує натискання на кнопку "База словників".
    Відправляє користувачу словники у вигляді кнопок.
    """
    user_id: int = callback.from_user.id

    current_page: int = callback_data.page  # Поточна сторінка
    limit: int = callback_data.limit  # Ліміт словників на сторінці

    vocabs_lst: list = []  # Список всіх словників

    with Session() as db:
        user_vocabs: Query[Vocabulary] = get_user_vocabs_by_user_id(db, user_id)  # Словники користувача

        is_vocab_base_empty: bool = user_vocabs.first() is None

        if is_vocab_base_empty:
            msg_finally: str = MSG_ERROR_VOCAB_BASE_EMPTY
        else:
            msg_finally: str = MSG_ENTER_VOCAB

        for vocab in user_vocabs:
            vocab_id: Column[int] = vocab.id

            vocabs_dct: dict = get_vocabs_dict(vocab_id, db)  # Словник із словниковими парами
            vocabs_lst.append(vocabs_dct)  # Додавання словника до списку словників

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
    kb: InlineKeyboardMarkup = get_inline_kb_vocab_base(vocabs_lst,
                                                        start_offset,
                                                        end_offset,
                                                        current_page,
                                                        total_pages_pagination,
                                                        limit,
                                                        is_vocab_base_empty)

    await callback.message.edit_text(text=msg_finally, reply_markup=kb)


def get_vocabs_dict(vocab_id: int, db: sqlalchemy.orm.session.Session) -> dict:
    """Повертає згенерований словник для одного словника з словниковими парами"""
    vocab: Query[Vocabulary] | None = get_user_vocabs_by_vocab_id(db, vocab_id)

    # Перевірка, чи існує словник
    if not vocab:
        return {}

    # Структура для зберігання даних словника
    vocabs_dct: dict[str, Any] = {
        'id': vocab.id,
        'name': vocab.name,
        'wordpairs': []}

    # Всі словникові пари словника
    wordpairs: list = db.query(WordPair).filter(WordPair.vocabulary_id == vocab.id).all()

    for pair in wordpairs:
        # Слова з транскрипціями
        words: list[tuple] | list = db.query(Word.word, Word.transcription).join(
            WordPairWord, Word.id == WordPairWord.word_id).filter(
            WordPairWord.wordpair_id == pair.id).all()

        # Переклади з транскрипціями
        translations: list[tuple] | list = db.query(Translation.translation, Translation.transcription).join(
            WordPairTranslation, Translation.id == WordPairTranslation.translation_id).filter(
            WordPairTranslation.wordpair_id == pair.id).all()

        # Структура пари слів з транскрипціями
        wordpair_dict: dict[str[tuple | None]] = {
            'word': words[0][0] if words else None,
            'word_transcription': words[0][1] if words and words[0][1] else None,
            'translation': translations[0][0] if translations else None,
            'translation_transcription': translations[0][1] if translations and translations[0][1] else None}

        if pair.annotation:
            wordpair_dict['annotation'] = pair.annotation

        vocabs_dct['wordpairs'].append(wordpair_dict)
    return vocabs_dct
