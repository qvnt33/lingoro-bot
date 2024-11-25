import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

TOKEN: str | None = os.getenv('TOKEN')  # Токен API Telegram
DATABASE_URL = 'sqlite:///database.db'

# Налаштування словника
WORDPAIR_SEPARATOR = ':'  # Символ, який використовується для розділення словникових пар
WORDPAIR_ITEM_SEPARATOR = ','  # Символ, який використовується для розділення елементів (слів або перекладів)
WORDPAIR_TRANSCRIPTION_SEPARATOR = '|'  # Символ, який використовується для розділення слова та транскрипції
ALLOWED_CHARS: tuple[str, ...] = ('-', '_', ' ')  # Дозволені символи для назви словника та словникових пар

# Довжина назви словника
MIN_LENGTH_VOCAB_NAME = 3  # Мінімальна кількість символів у "назві словника"
MAX_LENGTH_VOCAB_NAME = 50  # Максимальна кількість символів у "назві словника"

# Довжина примітки до словника
MIN_LENGTH_VOCAB_DESCRIPTION = 3  # Мінімальна кількість символів у "примітці до словника"
MAX_LENGTH_VOCAB_DESCRIPTION = 100  # Максимальна кількість символів у "примітці до словника"

# Кількість слів у словниковій парі
MIN_COUNT_WORDPAIR_ITEMS = 1  # Мінімальна кількість "слів"
MAX_COUNT_WORDPAIR_ITEMS = 30  # Максимальна кількість "слів"

# Довжина слів в словниковій парі
MIN_LENGTH_WORDPAIR_COMPONENT = 1  # Мінімальна кількість символів
MAX_LENGTH_WORDPAIR_COMPONENT = 30  # Максимальна кількість символів

# Повідомлення для кастомних виключень
INVALID_VOCAB_INDEX_ERROR = 'Словника з ID "{id}" не знайдено у базі даних.'
USER_NOT_FOUND_ERROR = 'Користувача з ID "{id}" не знайдено у базі даних.'
WORDPAIR_NOT_FOUND_ERROR = 'Словникова пара з ID "{id}" не знайдено у базі даних.'
