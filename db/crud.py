from typing import Any

from sqlalchemy.orm import Session

from db.models import Translation, User, Vocabulary, Word, Wordpair, WordpairTranslation, WordpairWord
from exceptions import InvalidVocabIndexError, UserNotFoundError
from text_data import INVALID_VOCAB_INDEX_ERROR, USER_NOT_FOUND_ERROR


class UserCRUD:
    """Клас для CRUD-операцій з користувачами в БД"""

    def __init__(self, session: Session) -> None:
        self.session: Session = session

    def create_new_user(self, tg_user_data: User | None) -> None:
        """Створює нового користувача в БД.

        Args:
            tg_user_data (User | None): Вся telegram-інформація про користувача
            (message.from_user / callback.from_user).

        Returns:
            None
        """
        new_user = User(user_id=tg_user_data.id,
                        username=tg_user_data.username,
                        first_name=tg_user_data.first_name,
                        last_name=tg_user_data.last_name)
        self.session.add(new_user)
        self.session.commit()

    def check_user_exists_in_db(self, user_id: int) -> bool:
        """Перевіряє, чи є користувач в БД"""
        user: User | None = self.session.query(User).filter(
            User.user_id == user_id).first()
        return user is not None


class VocabCRUD:
    """Клас для CRUD-операцій з словниками в БД"""

    def __init__(self, session: Session) -> None:
        self.session: Session = session

    def create_new_vocab(self,
                         user_id: int,
                         vocab_name: str,
                         vocab_description: str | None,
                         vocab_wordpairs: list[dict]) -> None:
        """Додає новий користувацький словник та його словникові пари до БД.

        Args:
            user_id (int): ID користувача.
            vocab_name (str): Назва користувацького словника.
            vocab_description (str | None): Опис користувацького словника (може бути None).
            vocab_wordpairs (list[dict]): Список словникових пар із розділеними компонентами у
            форматі python-словника.
                Приклад (vocab_wordpairs):
                [
                    {
                        'words': [
                            {'word': 'cat', 'transcription': None},
                            ],
                        'translations': [
                            {'translation': 'кіт', 'transcription': None},
                            ],
                        'annotation': None
                    },
                    {
                        'words': [
                            {'word': 'hello', 'transcription': 'хелоу'},
                            {'word': 'hi', 'transcription': 'хай'},
                            ],
                        'translations': [
                            {'translation': 'привіт', 'transcription': None},
                            {'translation': 'вітаю', 'transcription': None},
                            ],
                        'annotation': 'загальна форма вітання'
                    }
                ]

        Returns:
            None
        """
        user: User | None = self.session.query(User).filter(
            User.user_id == user_id).first()

        if user is None:
            raise UserNotFoundError(USER_NOT_FOUND_ERROR.format(id=self.user_id))

        # Створення нового словника
        new_vocab = Vocabulary(name=vocab_name,
                               description=vocab_description,
                               user_id=user_id)
        self.session.add(new_vocab)
        self.session.commit()

        vocab_id: int = new_vocab.id

        # Додавання словникових пар та звʼязків між словами та перекладами
        for wordpair_item in vocab_wordpairs:
            wordpair_words: list[dict] = wordpair_item.get('words')
            wordpair_translations: list[dict] = wordpair_item.get('translations')
            annotation: str | None = wordpair_item.get('annotation')

            new_wordpair = Wordpair(annotation=annotation,
                                    vocabulary_id=vocab_id)
            self.session.add(new_wordpair)
            self.session.commit()

            wordpair_id: int = new_wordpair.id

            # Додавання слів та перекладів до БД
            self._add_wordpair_words(wordpair_words, wordpair_id)
            self._add_wordpair_translations(wordpair_translations, wordpair_id)

    def _add_wordpair_words(self, wordpair_words: list[dict], wordpair_id: int) -> None:
        """Додає слова словникової пари до БД.
        Одразу звʼязує їх з словниковою парою по "wordpair_id".

        Args:
            wordpair_words (list[dict]):
                Приклад (wordpair_words):
                [
                    {'word': 'hello', 'transcription': 'хелоу'},
                    {'word': 'hi', 'transcription': 'хай'},
                ]
            wordpair_id (int): ID словникової пари, якій належать слова.

        Returns:
            None
        """
        for word_item in wordpair_words:
            word: str = word_item.get('word')
            transcription: str | None = word_item.get('transcription')

            new_word = Word(word=word,
                            transcription=transcription)
            self.session.add(new_word)
            self.session.commit()

            # Звʼязування слова та словникової пари
            new_wordpair_word = WordpairWord(word_id=new_word.id,
                                             wordpair_id=wordpair_id)
            self.session.add(new_wordpair_word)
        self.session.commit()

    def _add_wordpair_translations(self, wordpair_translations: list[dict], wordpair_id: int) -> None:
        """Додає переклади словникової пари до БД.
        Одразу звʼязує їх з словниковою парою по ID.

        Args:
            wordpair_translations (list[dict]):
                Приклад:
                [
                    {'translation': 'привіт', 'transcription': None},
                    {'translation': 'доброго дня', 'transcription': None},
                ]
            wordpair_id (int): ID словникової пари, якій належать переклади.

        Returns:
            None
        """
        for translation_item in wordpair_translations:
            translation: str = translation_item.get('translation')
            transcription: str | None = translation_item.get('transcription')

            new_translation = Translation(translation=translation,
                                          transcription=transcription)
            self.session.add(new_translation)
            self.session.commit()

            # Звʼязування перекладу та словникової пари
            new_wordpair_translation = WordpairTranslation(translation_id=new_translation.id,
                                                           wordpair_id=wordpair_id)
            self.session.add(new_wordpair_translation)
        self.session.commit()

    def get_all_vocabs_data(self, user_id: int) -> list[dict]:
        """Повертає дані всіх користувацьких словників.
        За допомогою ID користувача.

        Args:
            user_id (int): ID користувача.

        Returns:
            list[dict]: Дані всіх користувацьких словників у вигляді списку з python-словниками.

        Examples:
            >>> get_all_vocabs_data(user_id=1)
                [
                    {
                        'words': [
                            {'word': 'cat', 'transcription': None},
                            ],
                        'translations': [
                            {'translation': 'кіт', 'transcription': None},
                            ],
                        'annotation': None
                    },
                    {
                        'words': [
                            {'word': 'hello', 'transcription': 'хелоу'},
                            {'word': 'hi', 'transcription': 'хай'},
                            ],
                        'translations': [
                            {'translation': 'привіт', 'transcription': None},
                            {'translation': 'вітаю', 'transcription': None},
                            ],
                        'annotation': 'загальна форма вітання'
                    }
                ]
        """
        all_vocabs: list[Vocabulary] = self.session.query(Vocabulary).filter(
            Vocabulary.user_id == user_id).all()

        all_vocabs_data: list[dict] = []

        for vocab_item in all_vocabs:
            vocab_id: int = vocab_item.id
            vocab_data: dict[str, Any] = self.get_vocab_data(vocab_id)
            all_vocabs_data.append(vocab_data)
        return all_vocabs_data

    def get_vocab_data(self, vocab_id: int) -> dict[str, Any]:
        """Повертає дані користувацького словника.
        За допомогою ID словника.

        Args:
            vocab_id (int): ID користувацького словника.

        Returns:
            dict[str, Any]: Дані користувацького словника у вигляді python-словника.

        Examples:
            >>> get_vocab_data(vocab_id=1)
                {
                    'words': [
                        {'word': 'cat', 'transcription': None},
                        ],
                    'translations': [
                        {'translation': 'кіт', 'transcription': None},
                        ],
                    'annotation': None
                }
        """
        vocab: Vocabulary | None = self.session.query(Vocabulary).filter(
            Vocabulary.id == vocab_id).first()

        if vocab is None:
            raise InvalidVocabIndexError(INVALID_VOCAB_INDEX_ERROR.format(id=vocab_id))

        all_wordpairs: list[Wordpair] = self.session.query(Wordpair).filter(
                Wordpair.vocabulary_id == vocab_id).all()
        wordpairs_count: int = len(all_wordpairs)

        vocab_data: dict[str, Any] = {'id': vocab.id,
                                      'name': vocab.name,
                                      'description': vocab.description,
                                      'number_errors': vocab.number_errors,
                                      'wordpairs_count': wordpairs_count}
        return vocab_data

    def delete_vocab(self, vocab_id: int) -> None:
        """Видаляє користувацький словник.
        За допомогою ID словника.
        Словникові пари та вся інформація залишається у БД.
        """
        vocab: Vocabulary | None = self.session.query(Vocabulary).filter(
            Vocabulary.id == vocab_id).first()

        if vocab is None:
            raise InvalidVocabIndexError(INVALID_VOCAB_INDEX_ERROR.format(id=vocab.id))

        self.session.delete(vocab)
        self.session.commit()


class WordpairCRUD:
    """Клас для CRUD-операцій з словниковими парами в БД"""

    def __init__(self, session: Session) -> None:
        self.session: Session = session

    def get_wordpairs(self, vocab_id: int) -> list[dict]:
        """Повертає список словникових пар за "vocab_id".

        Args:
            vocab_id (int): ID користувацького словника.

        Returns:
            list[dict]: Список з всією інформацією (слова, переклади, анотація, к-сть помилок під час тренування)
            про всі словникові пари, які належать користувацькому словнику по переданному ID у вигляді python-словників.

        Examples:
            >>> get_wordpairs_by_vocab_id(vocab_id=1)
                [
                    {
                        'words': [
                            {'word': 'cat', 'transcription': 'кет'},
                            ],
                        'translations': [
                            {'translation': 'кіт', 'transcription': None},
                            ],
                        'annotation': None,
                        'number_errors': 0
                    },
                ]
        """
        wordpair_query: list[Wordpair] = self.session.query(Wordpair).filter(
            Wordpair.vocabulary_id == vocab_id).all()

        all_wordpairs: list[dict] = []

        for wordpair in wordpair_query:
            words: list[dict] = self._get_words_with_transcriptions(wordpair.id)
            translations: list[dict] = self._get_translations_with_transcriptions(wordpair.id)
            annotation: str | None = wordpair.annotation
            number_errors: int = wordpair.number_errors

            wordpair_components: dict[str, Any] = {'words': words,
                                                   'translations': translations,
                                                   'annotation': annotation,
                                                   'number_errors': number_errors}
            all_wordpairs.append(wordpair_components)

        return all_wordpairs

    def _get_words_with_transcriptions(self, wordpair_id: int) -> list[dict]:
        """Повертає список слів та їх транскрипцій зі словникової пари за "wordpair_id".

        Args:
            wordpair_id (int): ID словникової пари.

        Returns:
            list[dict]: Список з всіма словами та їх транскрипцією, які належать словниковій парі по переданному ID
            у вигляді python-словників.

        Examples:
            >>> _get_words_with_transcriptions(wordpair_id=1)
                [
                    {'word': cat,
                    'transcription': 'кет'},
                ]
        """
        all_wordpair_words: list[WordpairWord] = self.session.query(WordpairWord).filter(
            WordpairWord.wordpair_id == wordpair_id).all()
        words_with_transcriptions: list[dict] = []

        for word in all_wordpair_words:
            word_query: Word | None = self.session.query(Word).filter(
                Word.id == word.word_id).first()
            words_with_transcriptions.append({'word': word_query.word,
                                              'transcription': word_query.transcription})
        return words_with_transcriptions

    def _get_translations_with_transcriptions(self, wordpair_id: int) -> list[dict]:
        """Повертає список перекладів та їх транскрипцій зі словникової пари за "wordpair_id".

        Args:
            wordpair_id (int): ID словникової пари.

        Returns:
            list[dict]: Список з всіма перекладами та їх транскрипцією, які належать словниковій парі по переданному ID
            у вигляді python-словників.

        Examples:
            >>> _get_translations_with_transcriptions(wordpair_id=1)
                [
                    {'translation': кіт,
                    'transcription': None},
                ]
        """
        all_wordpair_translations: list[WordpairWord] = self.session.query(WordpairTranslation).filter(
            WordpairTranslation.wordpair_id == wordpair_id).all()
        translations_with_transcriptions: list[dict] = []

        for translation in all_wordpair_translations:
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
        wordpair_word_query: list[WordpairWord] = db.query(WordpairWord).filter(
            WordpairWord.wordpair_id == wordpair.id).all()
        for wordpair_word in wordpair_word_query:
            word_query: Word | None = db.query(Word).filter(Word.id == wordpair_word.word_id).first()
            words_lst.append((word_query.word, word_query.transcription))

        # Всі переклади словникової пари
        wordpair_translation_query: list[WordpairTranslation] = db.query(WordpairTranslation).filter(
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
