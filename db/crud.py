from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from db.models import Translation, User, Vocabulary, Word, Wordpair, WordpairTranslation, WordpairWord
from exceptions import UserNotFoundError


class UserCRUD:
    """Клас для CRUD-операцій з користувачами в БД"""

    def __init__(self, session: Session) -> None:
        self.session: Session = session

    def add_new_user_to_db(self, tg_user_data: User | None) -> None:
        """Створює нового користувача в БД"""
        new_user = User(user_id=tg_user_data.id,
                        username=tg_user_data.username,
                        first_name=tg_user_data.first_name,
                        last_name=tg_user_data.last_name)
        self.session.add(new_user)
        self.session.commit()

    def check_user_exists_in_db(self, user_id: int) -> bool:
        """Перевіряє, чи є користувач в БД"""
        user_query: User | None = self.session.query(User).filter(
            User.user_id == user_id).first()
        return user_query is not None


class VocabCRUD:
    """Клас для CRUD-операцій з словниками в БД"""

    def __init__(self, session: Session, user_id: int) -> None:
        self.session: Session = session
        self.user_id: int = user_id

    def add_vocab_to_db(self,
                        vocab_name: str,
                        vocab_description: str | None,
                        wordpair_components: list[dict]) -> None:
        """Додає новий словник та його словникові пари до БД"""
        user: User | None = self.session.query(User).filter(
            User.user_id == self.user_id).first()

        # Якщо користувача немає в БД
        if user is None:
            raise UserNotFoundError(f'Користувача з ID "{self.user_id}" не знайдено у БД')

        # Створення нового словника
        new_vocab = Vocabulary(name=vocab_name,
                               description=vocab_description,
                               user_id=self.user_id)
        self.session.add(new_vocab)
        self.session.commit()

        vocab_id: int = new_vocab.id

        # Додавання словникових пар та звʼязків між словами та перекладами
        for wordpair in wordpair_components:
            wordpair_words: list[dict] = wordpair['words']
            wordpair_translations: list[dict] = wordpair['translations']
            annotation: str | None = wordpair['annotation']

            # Створення словникової пари
            new_wordpair = Wordpair(annotation=annotation,
                                    vocabulary_id=vocab_id)
            self.session.add(new_wordpair)
            self.session.commit()

            wordpair_id: int = new_wordpair.id

            # Додавання слів та перекладів до БД
            self._add_wordpair_words_to_db(wordpair_words, wordpair_id)
            self._add_wordpair_translations_to_db(wordpair_translations, wordpair_id)

    def _add_wordpair_words_to_db(self,
                                  wordpair_words: list[dict],
                                  wordpair_id: int) -> None:
        """Додає слова словникової пари до БД"""
        for word_item in wordpair_words:
            word: str = word_item['word']
            word_transcription: str | None = word_item['transcription']

            new_word = Word(word=word,
                            transcription=word_transcription)
            self.session.add(new_word)
            self.session.commit()

            word_id: int = new_word.id

            # Звʼязування слова та словникової пари
            new_wordpair_word = WordpairWord(word_id=word_id,
                                             wordpair_id=wordpair_id)
            self.session.add(new_wordpair_word)
        self.session.commit()

    def _add_wordpair_translations_to_db(self,
                                         wordpair_translations: list[dict],
                                         wordpair_id: int) -> None:
        """Додає переклади словникової пари до БД"""
        for translation_item in wordpair_translations:
            translation: str = translation_item['translation']
            translation_transcription: str | None = translation_item['transcription']

            new_translation = Translation(translation=translation,
                                          transcription=translation_transcription)
            self.session.add(new_translation)
            self.session.commit()

            translation_id: int = new_translation.id

            # Звʼязування перекладу та словникової пари
            new_wordpair_translation = WordpairTranslation(translation_id=translation_id,
                                                           wordpair_id=wordpair_id)
            self.session.add(new_wordpair_translation)
        self.session.commit()

    def get_user_vocab(self) -> Vocabulary | None:
        """Повертає словник користувача з БД"""
        vocab_query: Query[Vocabulary] = self.session.query(Vocabulary).filter(
            Vocabulary.user_id == self.user_id)
        return vocab_query.first()

    def get_user_all_vocabs(self) -> list[Vocabulary]:
        """Повертає всі словники користувача з БД"""
        vocab_query: Query[Vocabulary] = self.session.query(Vocabulary).filter(
            Vocabulary.user_id == self.user_id)
        return vocab_query.all()


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
