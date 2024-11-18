from datetime import datetime
from typing import Any

from .database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.orm.relationships import _RelationshipDeclared


class User(Base):
    """Таблиця користувачів"""

    __tablename__: str = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)

    username = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))

    created_at = Column(DateTime(timezone=True),
                        default=datetime.now())

    # Відношення до Vocabulary (для каскадного видалення)
    # Видалення всіх пов'язаних словників (Vocabulary), якщо видаляється User
    vocabularies: _RelationshipDeclared[Any] = relationship('Vocabulary',
                                                            backref='user',
                                                            cascade='all, delete-orphan')


class Vocabulary(Base):
    """Таблиця словників"""

    __tablename__ = 'vocabularies'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(100))
    number_errors = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), default=datetime.now())
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Відношення до Wordpair (passive_deletes=True)
    # Дозволяє базі даних керувати видаленням дочірніх записів без додаткових запитів
    wordpairs: _RelationshipDeclared[Any] = relationship(
        'Wordpair',
        backref='vocabulary',
        cascade='all, delete-orphan',
        passive_deletes=True,  # Уникає додаткових запитів до бази при видаленні
    )


class Wordpair(Base):
    """Таблиця словникових пар словника"""

    __tablename__: str = 'wordpairs'

    id = Column(Integer, primary_key=True)
    annotation = Column(String(50))
    number_errors = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True),
                        default=datetime.now())

    vocabulary_id = Column(Integer, ForeignKey('vocabularies.id'), nullable=False)

    # Відношення до WordpairWord та WordpairTranslation (для каскадного видалення)
    # Видалення всіх пов'язаних словників (WordpairWord, WordpairTranslation), якщо видаляється Wordpair
    wordpair_words: _RelationshipDeclared[Any] = relationship('WordpairWord',
                                                              cascade='all, delete-orphan')
    wordpair_translations: _RelationshipDeclared[Any] = relationship('WordpairTranslation',
                                                                     cascade='all, delete-orphan')


class WordpairWord(Base):
    """Таблиця зв'язків між словниковими парами та словами"""

    __tablename__: str = 'wordpair_words'

    id = Column(Integer, primary_key=True)

    # ondelete='CASCADE' забезпечує автоматичне видалення записів з WordpairWord,
    # якщо видаляється відповідний Word або Wordpair
    word_id = Column(Integer, ForeignKey('words.id', ondelete='CASCADE'), nullable=False)
    wordpair_id = Column(Integer, ForeignKey('wordpairs.id', ondelete='CASCADE'), nullable=False)


class WordpairTranslation(Base):
    """Таблиця зв'язків між словниковими парами та перекладами"""

    __tablename__: str = 'wordpair_translations'

    id = Column(Integer, primary_key=True)

    # ondelete='CASCADE' забезпечує автоматичне видалення записів з WordpairTranslation,
    # якщо видаляється відповідний Translation або Wordpair
    translation_id = Column(Integer, ForeignKey('translations.id', ondelete='CASCADE'), nullable=False)
    wordpair_id = Column(Integer, ForeignKey('wordpairs.id', ondelete='CASCADE'), nullable=False)


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
