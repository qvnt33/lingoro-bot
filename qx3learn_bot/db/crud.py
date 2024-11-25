from sqlalchemy.orm import Session

from qx3learn_bot.config import INVALID_VOCAB_INDEX_ERROR, USER_NOT_FOUND_ERROR
from qx3learn_bot.custom_types.vocab_types import VocabDataType
from qx3learn_bot.custom_types.wordpair_types import (
    WordpairInfoType,
    WordpairTranslationType,
    WordpairType,
    WordpairWordType,
)
from qx3learn_bot.db.models import (
    TrainingSession,
    Translation,
    User,
    Vocabulary,
    Word,
    Wordpair,
    WordpairTranslation,
    WordpairWord,
)
from qx3learn_bot.exceptions import InvalidVocabIndexError, UserNotFoundError


class UserCRUD:
    """Клас для CRUD-операцій з користувачами в БД"""

    def __init__(self, session: Session) -> None:
        self.session: Session = session

    def create_new_user(self, tg_user_data: User) -> None:
        """Створює нового користувача в БД.

        Args:
            tg_user_data (User): Вся telegram-інформація про користувача
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
                         vocab_wordpairs: list[WordpairType]) -> None:
        """Додає новий користувацький словник та його словникові пари до БД.

        Args:
            user_id (int): ID користувача.
            vocab_name (str): Назва користувацького словника.
            vocab_description (str | None): Опис користувацького словника (може бути None).
            vocab_wordpairs (list[WordpairType]): Список словникових пар із розділеними компонентами у
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
            raise UserNotFoundError(USER_NOT_FOUND_ERROR.format(id=user_id))

        # Створення нового словника
        new_vocab = Vocabulary(name=vocab_name,
                               description=vocab_description,
                               user_id=user_id)
        self.session.add(new_vocab)
        self.session.commit()

        vocab_id: int = new_vocab.id

        # Додавання словникових пар та звʼязків між словами та перекладами
        for wordpair_item in vocab_wordpairs:
            wordpair_words: list[WordpairWordType] | None = wordpair_item.get('words')
            if wordpair_words is None:
                raise ValueError('Ключ "words" відсутній або None')

            wordpair_translations: list[WordpairTranslationType] | None = wordpair_item.get('translations')
            if wordpair_translations is None:
                raise ValueError('Ключ "translations" відсутній або None')

            annotation: str | None = wordpair_item.get('annotation')

            new_wordpair = Wordpair(annotation=annotation,
                                    vocabulary_id=vocab_id)
            self.session.add(new_wordpair)
            self.session.commit()

            wordpair_id: int = new_wordpair.id

            # Додавання слів та перекладів до БД
            self._add_wordpair_words(wordpair_words, wordpair_id)
            self._add_wordpair_translations(wordpair_translations, wordpair_id)

    def _add_wordpair_words(self, wordpair_words: list[WordpairWordType], wordpair_id: int) -> None:
        """Додає слова словникової пари до БД.
        Одразу звʼязує їх з словниковою парою по "wordpair_id".

        Args:
            wordpair_words (list[WordpairWordType]):
                Приклад (wordpair_words):
                [
                    {'word': 'hello', 'transcription': 'хелоу'},
                    {'word': 'hi', 'transcription': None},
                ]
            wordpair_id (int): ID словникової пари, якій належать слова.

        Returns:
            None
        """
        for word_item in wordpair_words:
            word: str | None = word_item.get('word')
            if word is None:
                raise ValueError('Ключ "word" відсутній або None')

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

    def _add_wordpair_translations(self,
                                   wordpair_translations: list[WordpairTranslationType],
                                   wordpair_id: int) -> None:
        """Додає переклади словникової пари до БД.
        Одразу звʼязує їх з словниковою парою по ID.

        Args:
            wordpair_translations (list[WordpairTranslationType]):
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
            translation: str | None = translation_item.get('translation')
            if translation is None:
                raise ValueError('Ключ "translation" відсутній або None')

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

    def get_all_vocabs_data(self, user_id: int) -> list[VocabDataType]:
        """Повертає дані всіх користувацьких словників.
        За допомогою ID користувача.

        Args:
            user_id (int): ID користувача.

        Returns:
            list[VocabDataType]: Дані всіх користувацьких словників у вигляді списку з python-словниками.

        Examples:
            >>> get_all_vocabs_data(user_id=1)
                [
                    {
                    'id': 1,
                    'name': 'Тварини',
                    'description': None,
                    'number_errors': 0,
                    'created_at': '2024-11-17 10:12:35.123',
                    'wordpairs_count': 2
                    },
                ]
        """
        all_vocabs: list[Vocabulary] = self.session.query(Vocabulary).filter(
            Vocabulary.user_id == user_id,
            ~Vocabulary.is_deleted).all()

        all_vocabs_data: list[VocabDataType] = []

        for vocab_item in all_vocabs:
            vocab_id: int = vocab_item.id
            vocab_data: VocabDataType = self.get_vocab_data(vocab_id)
            all_vocabs_data.append(vocab_data)
        return all_vocabs_data

    def get_vocab_data(self, vocab_id: int) -> VocabDataType:
        """Повертає дані користувацького словника.
        За допомогою ID словника.

        Args:
            vocab_id (int): ID користувацького словника.

        Returns:
            VocabDataType: Дані користувацького словника у вигляді python-словника.

        Examples:
            >>> get_vocab_data(vocab_id=1)
                {
                    'id': 1,
                    'name': 'Тварини',
                    'description': None,
                    'number_errors': 0,
                    'created_at': '2024-11-17 10:12:35.123',
                    'wordpairs_count': 2
                }
        """
        vocab: Vocabulary | None = self.session.query(Vocabulary).filter(
            Vocabulary.id == vocab_id,
            ~Vocabulary.is_deleted).first()

        if vocab is None:
            raise InvalidVocabIndexError(INVALID_VOCAB_INDEX_ERROR.format(id=vocab_id))

        all_wordpairs: list[Wordpair] = self.session.query(Wordpair).filter(
                Wordpair.vocabulary_id == vocab_id).all()
        wordpairs_count: int = len(all_wordpairs)

        vocab_data: VocabDataType = {'id': vocab.id,
                                     'name': vocab.name,
                                     'description': vocab.description,
                                     'number_errors': vocab.number_errors,
                                     'created_at': vocab.created_at,
                                     'wordpairs_count': wordpairs_count}
        return vocab_data

    def soft_delete_vocab(self, vocab_id: int) -> None:
        """Мʼяко видаляє користувацький словник, позначаючи його як 'видалений' (.is_deleted=True)"""
        vocab: Vocabulary | None = self.session.query(Vocabulary).filter(
            Vocabulary.id == vocab_id).first()

        if vocab is None:
            raise InvalidVocabIndexError(INVALID_VOCAB_INDEX_ERROR.format(id=vocab_id))

        vocab.is_deleted = True
        self.session.commit()

    def delete_vocab(self, vocab_id: int) -> None:
        """Видаляє користувацький словник, словникові пари, та всі звʼязки"""
        # !NOT USED
        vocab: Vocabulary | None = self.session.query(Vocabulary).filter(
            Vocabulary.id == vocab_id).first()

        if vocab is None:
            raise InvalidVocabIndexError(INVALID_VOCAB_INDEX_ERROR.format(id=vocab_id))

        # Видалення всіх словникових пар, повʼязаних зі словником
        self._delete_wordpairs_by_vocab_id(vocab_id)

        # Видалення словника
        self.session.delete(vocab)
        self.session.commit()

        # Видалення невикористаних слів та перекладів
        self._delete_unused_words()
        self._delete_unused_translations()

    def _delete_wordpairs_by_vocab_id(self, vocab_id: int) -> None:
        """Видаляє всі словникові пари, повʼязані зі словником"""
        # !NOT USED
        wordpairs: list[Wordpair] = self.session.query(Wordpair).filter(
            Wordpair.vocabulary_id == vocab_id).all()

        for wordpair in wordpairs:
            # Видалення звʼязків слів та перекладів зі словниковою парою
            self.session.query(WordpairWord).filter(
                WordpairWord.wordpair_id == wordpair.id).delete(synchronize_session=False)
            self.session.query(WordpairTranslation).filter(
                WordpairTranslation.wordpair_id == wordpair.id).delete(synchronize_session=False)

            # Видалення словникової пари
            self.session.delete(wordpair)
        self.session.commit()

    def _delete_unused_words(self) -> None:
        """Видаляє всі слова, які більше не повʼязані зі словниковими парами"""
        # !NOT USED
        unused_words: list[Word] = self.session.query(Word).outerjoin(WordpairWord).filter(
            WordpairWord.id.is_(None)).all()
        for word in unused_words:
            self.session.delete(word)
        self.session.commit()

    def _delete_unused_translations(self) -> None:
        """Видаляє всі переклади, які більше не повʼязані зі словниковими парами"""
        # !NOT USED
        unused_translations: list[Translation] = self.session.query(Translation).outerjoin(WordpairTranslation).filter(
            WordpairTranslation.id.is_(None)).all()
        for translation in unused_translations:
            self.session.delete(translation)
        self.session.commit()


class WordpairCRUD:
    """Клас для CRUD-операцій з словниковими парами в БД"""

    def __init__(self, session: Session) -> None:
        self.session: Session = session

    def get_wordpairs(self, vocab_id: int) -> list[WordpairInfoType]:
        """Повертає список словникових пар за "vocab_id".

        Args:
            vocab_id (int): ID користувацького словника.

        Returns:
            list[WordpairInfoType]: Список з всією інформацією
            (слова, переклади, анотація, к-сть помилок під час тренування) про всі словникові пари,
            які належать користувацькому словнику по переданному ID у вигляді python-словників.

        Examples:
            >>> get_wordpairs(vocab_id=1)
                [
                    {
                        'id': 0,
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

        all_wordpairs: list[WordpairInfoType] = []

        for wordpair in wordpair_query:
            wordpair_id: int = wordpair.id
            words: list[WordpairWordType] = self._get_words_with_transcriptions(wordpair.id)
            translations: list[WordpairTranslationType] = self._get_translations_with_transcriptions(wordpair.id)
            annotation: str | None = wordpair.annotation
            number_errors: int = wordpair.number_errors

            wordpair_components: WordpairInfoType = {'id': wordpair_id,
                                                     'words': words,
                                                     'translations': translations,
                                                     'annotation': annotation,
                                                     'number_errors': number_errors}
            all_wordpairs.append(wordpair_components)
        return all_wordpairs

    def _get_words_with_transcriptions(self, wordpair_id: int) -> list[WordpairWordType]:
        """Повертає список слів та їх транскрипцій зі словникової пари за "wordpair_id".

        Args:
            wordpair_id (int): ID словникової пари.

        Returns:
            list[WordpairWordType]: Список з всіма словами та їх транскрипцією, які належать словниковій парі
            по переданному ID у вигляді python-словників.

        Examples:
            >>> _get_words_with_transcriptions(wordpair_id=1)
                [
                    {
                        'word': 'cat',
                        'transcription': 'кет'
                    },
                ]
        """
        all_wordpair_words: list[WordpairWord] = self.session.query(WordpairWord).filter(
            WordpairWord.wordpair_id == wordpair_id).all()

        words_with_transcriptions: list[WordpairWordType] = []

        for word in all_wordpair_words:
            word_query: Word | None = self.session.query(Word).filter(
                Word.id == word.word_id).first()

            if word_query is None:
                raise ValueError(f'Слово з ID {word.word_id} не знайдено в базі даних.')

            words_with_transcriptions.append({'word': word_query.word,
                                              'transcription': word_query.transcription})
        return words_with_transcriptions

    def _get_translations_with_transcriptions(self, wordpair_id: int) -> list[WordpairTranslationType]:
        """Повертає список перекладів та їх транскрипцій зі словникової пари за "wordpair_id".

        Args:
            wordpair_id (int): ID словникової пари.

        Returns:
            list[WordpairTranslationType]: Список з всіма перекладами та їх транскрипцією, які належать словниковій парі
            по переданному ID у вигляді python-словників.

        Examples:
            >>> _get_translations_with_transcriptions(wordpair_id=1)
                [
                    {
                        'translation': кіт,
                        'transcription': None
                    },
                ]
        """
        all_wordpair_translations: list[WordpairWord] = self.session.query(WordpairTranslation).filter(
            WordpairTranslation.wordpair_id == wordpair_id).all()

        translations_with_transcriptions: list[WordpairTranslationType] = []

        for translation in all_wordpair_translations:
            translation_query: Translation | None = self.session.query(Translation).filter(
                Translation.id == translation.translation_id).first()

            if translation_query is None:
                raise ValueError(f'Переклад з ID {translation.translation_id} не знайдено в базі даних.')

            translations_with_transcriptions.append({'translation': translation_query.translation,
                                                     'transcription': translation_query.transcription})
        return translations_with_transcriptions

    def increment_wordpair_error_count(self, wordpair_id: int) -> None:
        """Збільшує кількість помилок у словниковій парі на 1.

        Args:
            wordpair_id (int): ID словникової пари.
        """
        wordpair: Wordpair = self.session.query(Wordpair).filter(
            Wordpair.id == wordpair_id).first()

        wordpair.number_errors += 1
        self.session.commit()


class TrainingCRUD:
    """Клас для CRUD-операцій з сесіями тренування в БД"""

    def __init__(self, session: Session) -> None:
        self.session: Session = session

    def create_new_training_session(self,
                                    user_id: int,
                                    vocabulary_id: int,
                                    training_mode: str,
                                    start_time: str,
                                    end_time: str,
                                    number_correct_answers: int,
                                    number_wrong_answers: int,
                                    number_annotation_shown: int,
                                    number_translation_shown: int,
                                    is_completed: bool) -> None:
        """Створює нову сесію тренування для користувача.

        Args:
            user_id (int): ID користувача.
            vocabulary_id (int): ID словника, який використовується для тренування.
            training_mode (str): Режим тренування.
            start_time (str): Час початку тренування у форматі рядка.
            end_time (str): Час завершення тренування у форматі рядка.
            number_correct_answers (int): Кількість правильних відповідей під час тренування.
            number_wrong_answers (int): Кількість неправильних відповідей під час тренування.
            number_annotation_shown
            number_translation_shown
            is_completed (bool): Чи було тренування успішно завершене.

        Returns:
            None
        """
        new_training_session = TrainingSession(training_mode=training_mode,
                                               start_time=start_time,
                                               end_time=end_time,
                                               number_correct_answers=number_correct_answers,
                                               number_wrong_answers=number_wrong_answers,
                                               number_annotation_shown=number_annotation_shown,
                                               number_translation_shown=number_translation_shown,
                                               is_completed=is_completed,
                                               user_id=user_id,
                                               vocabulary_id=vocabulary_id)

        self.session.add(new_training_session)
        self.session.commit()
