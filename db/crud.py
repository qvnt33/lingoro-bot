import logging
from typing import List

from sqlalchemy import Column

from .models import Translation, User, Vocabulary, Word, WordPair, WordPairTranslation, WordPairWord
from sqlalchemy.orm import Session


def create_user(db: Session, telegram_user: User | None) -> None:
    """Створює нового користувача в БД"""
    user_id: Column[int] = telegram_user.id
    user = User(user_id=user_id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name)
    db.add(user)

    logging.info(f'Був доданий до БД користувач: {user_id}')

    db.commit()


def add_vocab_to_db(db: Session, user_id: int, vocab_name: str, vocab_note: str, wordpairs_data: list) -> None:
    """Додає новий словник, словникові пари, слова, переклади до БД"""
    is_user_exists: bool = get_user_by_user_id(db, user_id=user_id) is not None
    if not is_user_exists:
        raise ValueError(f'Користувача з ID {user_id} не знайдено')

    # Додавання словника
    vocab = Vocabulary(name=vocab_name, description=vocab_note, user_id=user_id)
    db.add(vocab)
    db.commit()

    # Додавання словникових пар та звʼязків між словами та перекладами
    for wordpair_data in wordpairs_data:
        words_lst: list = wordpair_data['words']  # Список кортежів слів і їх транскрипцій
        translations_lst: list = wordpair_data['translations']  # Список кортежів перекладів і їх транскрипцій
        annotation: str = wordpair_data['annotation'] or '–'  # Анотація (якщо є)

        wordpair = WordPair(annotation=annotation, vocabulary_id=vocab.id)  # Словникова пара
        db.add(wordpair)
        db.commit()

        # Додавання слів
        for word, transcription in words_lst:
            word_entry = Word(word=word, transcription=transcription)
            db.add(word_entry)
            db.commit()

            # Звʼязування слова та словникової пари
            wordpair_word = WordPairWord(word_id=word_entry.id, wordpair_id=wordpair.id)
            db.add(wordpair_word)

        # Додавання перекладів
        for translation, transcription in translations_lst:
            translation_entry = Translation(translation=translation, transcription=transcription)
            db.add(translation_entry)
            db.commit()

            # Звʼязування перекладу та словникової пари
            wordpair_translation = WordPairTranslation(translation_id=translation_entry.id, wordpair_id=wordpair.id)
            db.add(wordpair_translation)

    logging.info(f'Був доданий до БД словник "{vocab}". Користувач: {user_id}')
    db.commit()


def get_user_by_user_id(db: Session, user_id: int) -> User | None:
    """Повертає користувача за його user_id"""
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_vocab_by_user_id(db: Session, user_id: int, is_all: bool = False) -> User | None:
    """Повертає словник користувача за його user_id"""
    if is_all:
        return db.query(Vocabulary).filter(Vocabulary.user_id == user_id).all()
    return db.query(Vocabulary).filter(Vocabulary.user_id == user_id).first()


def get_user_vocab_by_vocab_id(db: Session, vocab_id: int, is_all: bool = False) -> User | None:
    """Повертає словник користувача за vocab_id"""
    if is_all:
        return db.query(Vocabulary).filter(Vocabulary.id == vocab_id).all()
    return db.query(Vocabulary).filter(Vocabulary.id == vocab_id).first()


def get_vocab_details_by_vocab_id(db: Session, vocab_id: int) -> dict:
    """Повертає назву та примітку словника за vocab_id"""
    vocab = db.query(Vocabulary).filter(Vocabulary.id == vocab_id).first()
    return {'name': vocab.name, 'note': vocab.description}


def get_vocab_details_by_user_id(db: Session, user_id: int) -> dict:
    """Повертає назву та примітку словника за vocab_id"""
    vocab = db.query(Vocabulary).filter(Vocabulary.user_id == user_id).first()
    return {'name': vocab.name, 'note': vocab.description}


def get_wordpairs_by_vocab_id(db: Session, vocab_id: int) -> list[dict]:
    """Повертає всі словникові пари за vocab_id"""
    result = []

    wordpair_query = db.query(WordPair).filter(WordPair.vocabulary_id == vocab_id).all()

    for wordpair in wordpair_query:
        words_lst = []  # Список з кортежами слів та транскрипцій
        translations_lst = []  # Список з кортежами перекладів та транскрипцій
        annotation = wordpair.annotation  # Анотація

        # Всі слова словникової пари
        wordpair_word_query: List[WordPairWord] = db.query(WordPairWord).filter(
            WordPairWord.wordpair_id == wordpair.id).all()
        for wordpair_word in wordpair_word_query:
            word_query: Word | None = db.query(Word).filter(Word.id == wordpair_word.word_id).first()
            words_lst.append((word_query.word, word_query.transcription))

        # Всі переклади словникової пари
        wordpair_translation_query: List[WordPairTranslation] = db.query(WordPairTranslation).filter(
            WordPairTranslation.wordpair_id == wordpair.id).all()
        for wordpair_translation in wordpair_translation_query:
            translation_query: Translation | None = db.query(Translation).filter(
                Translation.id == wordpair_translation.translation_id).first()
            translations_lst.append((translation_query.translation, translation_query.transcription))

        # Додаємо дані про словникову пару до результату
        wordpair_data = {
            'words': words_lst,
            'translations': translations_lst,
            'annotation': annotation}

        result.append(wordpair_data)
    return result
