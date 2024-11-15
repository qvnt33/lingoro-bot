from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from db.models import Translation, User, Vocabulary, Word, Wordpair, WordpairTranslation, WordpairWord
from exceptions import InvalidVocabIndexError, UserNotFoundError


class UserCRUD:
    """Клас для CRUD-операцій з користувачами в БД"""

    def __init__(self, session: Session) -> None:
        self.session: Session = session

    def create_new_user(self, tg_user_data: User | None) -> None:
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

    def __init__(self, session: Session) -> None:
        self.session: Session = session

    def create_new_vocab(self,
                         user_id: int,
                         vocab_name: str,
                         vocab_description: str | None,
                         vocab_wordpairs: list[dict]) -> None:
        """Додає новий словник та його словникові пари до БД.

        Args:
            user_id (int): ID користувача.
            vocab_name (str): Назва словника.
            vocab_description (str | None): Опис словника (може бути None).
            wordpair_components (list[dict]): Список словникових пар із розділеними компонентами у вигляді словника.

        Returns:
            None
        """
        user_query: User | None = self.session.query(User).filter(
            User.user_id == user_id).first()

        # Якщо користувача немає в БД
        if user_query is None:
            raise UserNotFoundError(f'Користувача з ID "{self.user_id}" не знайдено у БД')

        # Створення нового словника
        new_vocab = Vocabulary(name=vocab_name,
                               description=vocab_description,
                               user_id=user_id)
        self.session.add(new_vocab)
        self.session.commit()

        vocab_id: int = new_vocab.id

        # Додавання словникових пар та звʼязків між словами та перекладами
        for wordpair in vocab_wordpairs:
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
            self._add_wordpair_words(wordpair_words, wordpair_id)
            self._add_wordpair_translations(wordpair_translations, wordpair_id)

    def _add_wordpair_words(self,
                            wordpair_words: list[dict],
                            wordpair_id: int) -> None:
        """Додає слова словникової пари до БД"""
        for word_item in wordpair_words:
            word: str = word_item['word']
            transcription: str | None = word_item['transcription']

            new_word = Word(word=word,
                            transcription=transcription)
            self.session.add(new_word)
            self.session.commit()

            # Звʼязування слова та словникової пари
            new_wordpair_word = WordpairWord(word_id=new_word.id,
                                             wordpair_id=wordpair_id)
            self.session.add(new_wordpair_word)
        self.session.commit()

    def _add_wordpair_translations(self,
                                   wordpair_translations: list[dict],
                                   wordpair_id: int) -> None:
        """Додає переклади словникової пари до БД"""
        for translation_item in wordpair_translations:
            translation: str = translation_item['translation']
            transcription: str | None = translation_item['transcription']

            new_translation = Translation(translation=translation,
                                          transcription=transcription)
            self.session.add(new_translation)
            self.session.commit()

            # Звʼязування перекладу та словникової пари
            new_wordpair_translation = WordpairTranslation(translation_id=new_translation.id,
                                                           wordpair_id=wordpair_id)
            self.session.add(new_wordpair_translation)
        self.session.commit()

    def get_vocab_data_by_id(self, vocab_id: int) -> dict:
        """Повертає словник за його ID зі всіма даними"""
        vocab_query: list[Vocabulary] = self.session.query(Vocabulary).filter(
            Vocabulary.id == vocab_id).first()
        wordpair_query: list[Wordpair] = self.session.query(Wordpair).filter(
                Wordpair.vocabulary_id == vocab_id).all()

        # Якщо у користувача немає словників
        if vocab_query is None:
            raise InvalidVocabIndexError(f'У БД немає словника з ID "{vocab_id}"')

        vocab_data: dict = {}
        vocab_data['id'] = vocab_query.id
        vocab_data['name'] = vocab_query.name
        vocab_data['description'] = vocab_query.description
        vocab_data['number_errors'] = vocab_query.number_errors
        vocab_data['wordpairs_count'] = len(wordpair_query)

        return vocab_data

    def get_data_all_vocabs(self, user_id: int) -> list[dict]:
        """Повертає список всіх словників за ID користувача зі всіма даними"""
        vocab_query: list[Vocabulary] = self.session.query(Vocabulary).filter(
            Vocabulary.user_id == user_id).all()

        vocab_data: list[dict] = []

        for vocab in vocab_query:
            vocab_id: int = vocab.id

            wordpair_query: list[Wordpair] = self.session.query(Wordpair).filter(
                Wordpair.vocabulary_id == vocab_id).all()
            wordpairs_count: int = len(wordpair_query)
            vocab_data.append({'id': vocab.id,
                               'name': vocab.name,
                               'description': vocab.description,
                               'number_errors': vocab.number_errors,
                               'wordpairs_count': wordpairs_count})
        return vocab_data

    def get_all_vocabs_by_user_id(self, user_id: int) -> list[Vocabulary]:
        """Повертає всі словники користувача"""
        vocab_query: Query[Vocabulary] = self.session.query(Vocabulary).filter(
            Vocabulary.user_id == user_id)
        return vocab_query.all()

    def get_wordpairs_by_vocab_id(self, vocab_id: int) -> list[dict]:
        """Повертає список словникових пар за "vocab_id".

        Args:
            vocab_id (int): Ідентифікатор словника.

        Returns:
            list[dict]: Список з словниковими парами у вигляді словників.
        """
        wordpair_query: list[Wordpair] = self.session.query(Wordpair).filter(
            Wordpair.vocabulary_id == vocab_id).all()

        all_wordpairs: list[dict] = []

        for wordpair in wordpair_query:
            words: list[dict] = self._get_words_with_transcriptions(wordpair.id)
            translations: list[dict] = self._get_translations_with_transcriptions(wordpair.id)
            annotation: str | None = wordpair.annotation
            total_number_errors: int = wordpair.total_number_errors

            wordpair_components: dict = {}

            wordpair_components['words'] = words
            wordpair_components['translations'] = translations
            wordpair_components['annotation'] = annotation
            wordpair_components['total_number_errors'] = total_number_errors

            all_wordpairs.append(wordpair_components)

        return all_wordpairs

    def _get_words_with_transcriptions(self, wordpair_id: int) -> list[dict]:
        """Повертає список слів та їх транскрипцій зі словникової пари за "wordpair_id".

        Args:
            wordpair_id (int): Ідентифікатор словникової пари.

        Returns:
            list[dict]: Список з словами та їх транскрипцією у вигляді словника.
        """
        wordpair_word_query: list[WordpairWord] = self.session.query(WordpairWord).filter(
            WordpairWord.wordpair_id == wordpair_id).all()
        words_with_transcriptions: list[dict] = []

        for word in wordpair_word_query:
            word_query: Word | None = self.session.query(Word).filter(
                Word.id == word.word_id).first()
            words_with_transcriptions.append({'word': word_query.word,
                                              'transcription': word_query.transcription})
        return words_with_transcriptions

    def _get_translations_with_transcriptions(self, wordpair_id: int) -> list[dict]:
        """Повертає список перекладів та їх транскрипцій зі словникової пари за "wordpair_id".

        Args:
            wordpair_id (int): Ідентифікатор словникової пари.

        Returns:
            list[dict]: Список з перекладами та їх транскрипцією у вигляді словника.
        """
        wordpair_translation_query: list[WordpairWord] = self.session.query(WordpairTranslation).filter(
            WordpairTranslation.wordpair_id == wordpair_id).all()
        translations_with_transcriptions: list[dict] = []

        for translation in wordpair_translation_query:
            translation_query: Translation | None = self.session.query(Translation).filter(
                Translation.id == translation.translation_id).first()
            translations_with_transcriptions.append({'translation': translation_query.translation,
                                                     'transcription': translation_query.transcription})
        return translations_with_transcriptions



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
