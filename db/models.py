from datetime import datetime

from .database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String


class User(Base):
    """Таблиця користувачів"""

    __tablename__: str = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)

    username = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))

    created_at = Column(DateTime(timezone=True), default=datetime.now)


class Vocabulary(Base):
    """Таблиця словників"""

    __tablename__: str = 'vocabularies'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(100))
    number_errors = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=datetime.now)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)


class Wordpair(Base):
    """Таблиця словникових пар словника"""

    __tablename__: str = 'wordpairs'

    id = Column(Integer, primary_key=True)
    annotation = Column(String(50))
    number_errors = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), default=datetime.now)

    vocabulary_id = Column(Integer, ForeignKey('vocabularies.id'), nullable=False)


class WordpairWord(Base):
    """Таблиця зв'язків між словниковими парами та словами"""

    __tablename__: str = 'wordpair_words'

    id = Column(Integer, primary_key=True)

    word_id = Column(Integer, ForeignKey('words.id'), nullable=False)
    wordpair_id = Column(Integer, ForeignKey('wordpairs.id'), nullable=False)


class WordpairTranslation(Base):
    """Таблиця зв'язків між словниковими парами та перекладами"""

    __tablename__: str = 'wordpair_translations'

    id = Column(Integer, primary_key=True)

    translation_id = Column(Integer, ForeignKey('translations.id'), nullable=False)
    wordpair_id = Column(Integer, ForeignKey('wordpairs.id'), nullable=False)


class Word(Base):
    """Таблиця слів"""

    __tablename__: str = 'words'

    id = Column(Integer, primary_key=True)
    word = Column(String(50), nullable=False)
    transcription = Column(String(50))


class Translation(Base):
    """Таблиця перекладів"""

    __tablename__: str = 'translations'

    id = Column(Integer, primary_key=True)
    translation = Column(String(50), nullable=False)
    transcription = Column(String(50))


class TrainingSession(Base):
    """Таблиця сесій тренувань"""

    __tablename__: str = 'training_sessions'

    id = Column(Integer, primary_key=True)
    training_mode = Column(String(50))

    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))

    number_correct_answers = Column(Integer, default=0)
    number_wrong_answers = Column(Integer, default=0)

    is_completed = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    vocabulary_id = Column(Integer, ForeignKey('vocabularies.id'), nullable=False)
