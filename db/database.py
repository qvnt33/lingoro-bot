from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///database.db')  # Подключение к БД SQLite
Base = declarative_base()  # Создание базового класса для моделей
Session = Session(bind=engine)  # Создание сессии подключения к БД
