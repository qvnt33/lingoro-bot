from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey
from .database import Base, engine


class User(Base):
    """Пользователи"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))


class Dictionary(Base):
    """Словари пользователей"""
    __tablename__ = 'dictionaries'

    id = Column(Integer, primary_key=True)
    dictionary_name = Column(String(50))  # Название словаря

    wordpair_count = Column(Integer, default=0)  # Кол-во словарных пар в словаре
    created_date = Column(Date)  # Дата создания словаря
    note = Column(String(100))  # Заметка к словарю
    user_id = Column(String(50), ForeignKey('users.id'))  # user_id пользователя


class Training(Base):
    """Вся информация о тренировках"""
    __tablename__ = 'training'

    id = Column(Integer, primary_key=True)
    training_mode = Column(String(50))  # Режим тренировки
    training_date = Column(Date)  # Дата тренировки

    error_count = Column(Integer)  # Кол-во ошибок за тренировку
    total_score = Column(Float)  # Общий балл за тренировку
    success_rate = Column(Float)  # Успешность тренировки (в процентах)

    # ID словаря, который тренировали
    dictionary_id = Column(Integer, ForeignKey('dictionaries.id'))


class WordPair(Base):
    """Словарные пары"""
    __tablename__ = 'wordpairs'

    id = Column(Integer, primary_key=True)
    word_1 = Column(String(100))  # Первое слово словаря
    word_2 = Column(String(100))  # Второе слово словаря

    # Аннотация к первому слову
    annotation_1 = Column(String(100), default=None)
    # Аннотация к второму слову
    annotation_2 = Column(String(100), default=None)

    # Кол-во всех ошибок словарной пары
    error_count = Column(Integer, default=0)

    # ID словаря, который тренировали
    dictionary_id = Column(Integer, ForeignKey('dictionaries.id'))


Base.metadata.create_all(bind=engine)  # Создание всех таблиц
