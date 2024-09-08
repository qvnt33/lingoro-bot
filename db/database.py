from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///database.db')  # Підключення до БД sqlite
Base = declarative_base()  # Створення базового класу для моделей
Session = Session(bind=engine)  # Створення сесії підключення до БД
