from typing import List

from sqlalchemy.orm import Session

from db.models import Translation, User, Vocabulary, Word, Wordpair, WordpairTranslation, WordpairWord
from exceptions import UserNotFoundError


def add_vocab_to_db(session: Session,
                    user_id: int,
                    vocab_name: str,
                    vocab_description: str | None,
                    wordpair_components: list[dict]) -> None:
    """!docstring Додає новий словник та його словникові пари до БД"""
    user: User | None = get_user_by_user_id(session, user_id)

    # Якщо користувача немає в БД
    if user is None:
        raise UserNotFoundError(f'Користувача з ID "{user_id}" не знайдено у БД')

    # Створення нового словника
    vocab_entry = Vocabulary(name=vocab_name,
                             description=vocab_description,
                             user_id=user_id)
    session.add(vocab_entry)
    session.commit()

    vocab_id: int = vocab_entry.id

    # Додавання словникових пар та звʼязків між словами та перекладами
    for wordpair in wordpair_components:
        wordpair_words: list[dict] = wordpair['words']
        wordpair_translations: list[dict] = wordpair['translations']
        annotation: str | None = wordpair['annotation']

        # Створення словникової пари
        wordpair_entry = Wordpair(annotation, vocab_id)
        session.add(wordpair_entry)
        session.commit()

        wordpair_id: int = wordpair_entry.id

        _add_wordpair_words_to_db(session, wordpair_words, wordpair_id)  # Додавання слів
        _add_wordpair_translations_to_db(session, wordpair_translations, wordpair_id)  # Додавання перекладів


def _add_wordpair_words_to_db(session: Session,
                              wordpair_words: list[dict],
                              wordpair_id: int) -> None:
    """Додає слова словникової пари до БД"""
    for word_item in wordpair_words:
        word: str = word_item['word']
        word_transcription: str | None = word_item['transcription']

        word_entry = Word(word=word,
                          transcription=word_transcription)
        session.add(word_entry)
        session.commit()

        word_id: int = word_entry.id

        # Звʼязування слова та словникової пари
        wordpair_word_entry = WordpairWord(word_id, wordpair_id)
        session.add(wordpair_word_entry)
    session.commit()


def _add_wordpair_translations_to_db(session: Session,
                                     wordpair_translations: list[dict],
                                     wordpair_id: int) -> None:
    """Додає переклади словникової пари до БД"""
    for translation_item in wordpair_translations:
        translation: str = translation_item['translation']
        translation_transcription: str | None = translation_item['transcription']

        translation_entry = Translation(translation=translation,
                                        transcription=translation_transcription)
        session.add(translation_entry)
        session.commit()

        translation_id: int = translation_entry.id

        # Звʼязування перекладу та словникової пари
        wordpair_translation_entry = WordpairTranslation(translation_id, wordpair_id)
        session.add(wordpair_translation_entry)
    session.commit()





def is_user_exists_in_db(session: Session, user_id: int) -> bool:
    """Перевіряє, чи є користувач у БД"""
    return session.query(User).filter(User.user_id == user_id).first() is not None


def create_user_in_db(session: Session, tg_user_data: User | None) -> None:
    """Створює нового користувача в БД"""
    user_entry = User(user_id=tg_user_data.id,
                      username=tg_user_data.username,
                      first_name=tg_user_data.first_name,
                      last_name=tg_user_data.last_name)
    session.add(user_entry)
    session.commit()

def get_user_by_user_id(session: Session, user_id: int) -> User | None:
    """Повертає користувача за його user_id"""
    return session.query(User).filter(User.user_id == user_id).first()


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


def get_wordpairs_by_vocab_id(db: Session, vocab_id: int) -> list[dict]:
    """Повертає всі словникові пари за vocab_id"""
    result = []

    wordpair_query = db.query(Wordpair).filter(Wordpair.vocabulary_id == vocab_id).all()

    for wordpair in wordpair_query:
        words_lst = []  # Список з кортежами слів та транскрипцій
        translations_lst = []  # Список з кортежами перекладів та транскрипцій
        annotation = wordpair.annotation  # Анотація

        # Всі слова словникової пари
        wordpair_word_query: List[WordpairWord] = db.query(WordpairWord).filter(
            WordpairWord.wordpair_id == wordpair.id).all()
        for wordpair_word in wordpair_word_query:
            word_query: Word | None = db.query(Word).filter(Word.id == wordpair_word.word_id).first()
            words_lst.append((word_query.word, word_query.transcription))

        # Всі переклади словникової пари
        wordpair_translation_query: List[WordpairTranslation] = db.query(WordpairTranslation).filter(
            WordpairTranslation.wordpair_id == wordpair.id).all()
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
