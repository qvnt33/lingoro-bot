from .database import Base, engine
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func


class User(Base):
    """Користувачі"""

    __tablename__: str = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)

    username = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())


class Vocabulary(Base):
    """Словники користувачів"""

    __tablename__: str = 'vocabularies'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))  # Назва словника
    note = Column(String(100))  # Нотатка до словника

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())  # Дата створення словника

    user_id = Column(Integer, ForeignKey('users.id'))  # user_id користувача


class WordPair(Base):
    """Словникові пари"""

    __tablename__: str = 'wordpairs'

    id = Column(Integer, primary_key=True)
    word_a = Column(String(100), nullable=False)  # Перше слово словникової пари
    word_b = Column(String(100), nullable=False)  # Друге слово словникової пари

    annotation_a = Column(String(100), default=None)  # Анотація до першого слова
    annotation_b = Column(String(100), default=None)  # Анотація до другого слова

    hint_a = Column(String(100))  # Підказка до першого слова
    hint_b = Column(String(100))  # Підказка до другого слова

    # Кількість помилок словникової пари за весь час
    error_count = Column(Integer, default=0)

    # ID словника, котрий використовували для тренування
    vocab_id = Column(Integer, ForeignKey('vocabularies.id'))


class VocabTraining(Base):
    """Уся інформація та статистика тренувань"""

    __tablename__: str = 'vocab_training'

    id = Column(Integer, primary_key=True)
    training_mode = Column(String(50))  # Тип тренування
    training_date = Column(DateTime(timezone=True),
                           server_default=func.now())  # Дата тренування

    error_count = Column(Integer)  # Кількість помилок за тренування
    total_score = Column(Float)  # Загальна оцінка тренування
    success_rate = Column(Float)  # Успішність тренування у відсотках

    # ID словника, котрий використовували для тренування
    vocab_id = Column(Integer, ForeignKey('vocabularies.id'))


Base.metadata.create_all(bind=engine)  # Створення усіх таблиць
