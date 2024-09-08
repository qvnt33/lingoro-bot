from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey
from .database import Base, engine


class User(Base):
    """Користувачі"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))

class Vocabulary(Base):
    """Словники користувачів"""
    __tablename__ = 'vocabularies'

    id = Column(Integer, primary_key=True)
    vocab_name = Column(String(50))  # Назва словника

    wordpair_count = Column(Integer, default=0)  # Кількість словникових пар у словнику
    created_date = Column(Date)  # Дата створення словника
    vocab_note = Column(String(100))  # Нотатка до словника

    user_id = Column(String(50), ForeignKey('users.id'))  # user_id користувача


class Training(Base):
    """Уся інформація та статистика про тренування"""
    __tablename__ = 'training'

    id = Column(Integer, primary_key=True)
    training_mode = Column(String(50))  # Тип тренування
    training_date = Column(Date)  # Дата тренування

    error_count = Column(Integer)  # Кількість помилок за тренування
    total_score = Column(Float)  # Загальна оцінка тренування
    success_rate = Column(Float)  # Успішність тренування у відсотках

    # ID словника, котрий використовували для тренування
    vocab_id = Column(Integer, ForeignKey('vocabularies.id'))


class WordPair(Base):
    """Словникові пари"""
    __tablename__ = 'wordpairs'

    id = Column(Integer, primary_key=True)
    word_1 = Column(String(100))  # Перше слово словника
    word_2 = Column(String(100))  # Друге слово словника

    # Анотація до першого слова
    annotation_1 = Column(String(100), default=None)
    # Анотація до другого слова
    annotation_2 = Column(String(100), default=None)

    # Кількість помилок словникової пари за весь час
    error_count = Column(Integer, default=0)

    # ID словника, котрий використовували для тренування
    vocab_id = Column(Integer, ForeignKey('vocabularies.id'))


Base.metadata.create_all(bind=engine)  # Створення усіх таблиць
