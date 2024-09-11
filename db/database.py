from typing import Any

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

engine: Engine = create_engine('sqlite:///database.db')  # Підключення до БД sqlite
Base: Any = declarative_base()  # Створення базового класу для моделей
Session = Session(bind=engine)  # Створення сесії підключення до БД
