import logging

from .models import User, Vocabulary
from sqlalchemy.orm import Session


def create_user(db: Session, telegram_user: User | None) -> User:
    """Створює нового користувача в БД"""
    user = User(user_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name)
    db.add(user)

    logging.info(f'Був доданий до БД користувач: {telegram_user.id}')

    db.commit()


def get_user_by_user_id(db: Session, user_id: int) -> User | None:
    """Повертає користувача за його user_id"""
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_vocabs_by_user_id(db: Session, user_id: int) -> User | None:
    """Повертає словник користувача за його user_id"""
    return db.query(Vocabulary).filter(Vocabulary.user_id == user_id)


def get_user_vocabs_by_vocab_id(db: Session, vocab_id: int) -> User | None:
    """Повертає словник користувача за vocab_id"""
    return db.query(Vocabulary).filter(Vocabulary.id == vocab_id).first()
