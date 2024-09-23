from datetime import datetime

from .database import Base, engine
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String


class User(Base):
    """Таблиця користувачів"""

    __tablename__: str = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)  # Унікальний ID користувача в Telegram

    username = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))

    created_at = Column(DateTime(timezone=True),
                        default=datetime.now())  # Дата додавання користувача до БД


class Vocabulary(Base):
    """Таблиця словників користувачів"""

    __tablename__: str = 'vocabularies'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)  # Назва словника
    description = Column(String(100))  # Опис словника
    vocabulary_errors = Column(Integer, default=0)  # Кількість помилок у словнику

    created_at = Column(DateTime(timezone=True),
                        default=datetime.now())  # Дата створення словника

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Зв'язок з користувачем


class WordPair(Base):
    """Таблиця словникових пар"""

    __tablename__: str = 'wordpairs'

    id = Column(Integer, primary_key=True)
    annotation = Column(String(50))  # Анотація до словникової пари
    wordpair_errors = Column(Integer, default=0)  # Кількість помилок у цій словниковій парі

    created_at = Column(DateTime(timezone=True),
                        default=datetime.now())  # Дата створення словникової пари

    vocabulary_id = Column(Integer, ForeignKey('vocabularies.id'), nullable=False)  # Зв'язок зі словником


class WordPairWords(Base):
    """Таблиця зв'язків між словниковими парами та словами"""

    __tablename__: str = 'wordpair_words'

    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey('words.id'), nullable=False)  # Зв'язок з таблицею слів
    wordpair_id = Column(Integer, ForeignKey('wordpairs.id'), nullable=False)  # Зв'язок зі словниковою парою


class Word(Base):
    """Таблиця слів"""

    __tablename__: str = 'words'

    id = Column(Integer, primary_key=True)
    word = Column(String(50), nullable=False)  # Слово


class WordPairTranslation(Base):
    """Таблиця зв'язків між словниковими парами та перекладами"""

    __tablename__: str = 'wordpair_translations'

    id = Column(Integer, primary_key=True)
    translation_id = Column(Integer, ForeignKey('translations.id'), nullable=False)  # Зв'язок з таблицею перекладів
    wordpair_id = Column(Integer, ForeignKey('wordpairs.id'), nullable=False)  # Зв'язок зі словниковою парою


class Translation(Base):
    """Таблиця перекладів"""

    __tablename__: str = 'translations'

    id = Column(Integer, primary_key=True)
    translation = Column(String(50), nullable=False)  # Переклад


class TrainingSession(Base):
    """Таблиця сесій тренувань"""

    __tablename__: str = 'training_sessions'

    id = Column(Integer, primary_key=True)
    training_mode = Column(String(50))  # Режим тренування

    start_time = Column(DateTime(timezone=True))  # Час початку тренування
    end_time = Column(DateTime(timezone=True), nullable=True)  # Час завершення тренування (NULL, якщо не завершене)

    correct_answers = Column(Integer, default=0)  # Кількість правильних відповідей
    wrong_answers = Column(Integer, default=0)  # Кількість неправильних відповідей

    is_completed = Column(Boolean, default=False)  # Чи було завершено тренування

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Зв'язок з користувачем
    vocabulary_id = Column(Integer, ForeignKey('vocabularies.id'), nullable=False)  # Зв'язок зі словником


def create_tables() -> None:
    """Функція для створення всіх таблиць у базі даних"""
    Base.metadata.create_all(bind=engine)
