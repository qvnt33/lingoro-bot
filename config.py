import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

TOKEN = os.getenv('TOKEN')  # Токен API Telegram
DATABASE_URL = 'sqlite:///database.db'

# Налаштування словника
DEFAULT_VOCAB_NOTE = 'Немає'  # Стандартна назва примітки до словника
WORDPAIR_SEPARATOR = ':'  # Символ, який використовується для розділення словникових пар
ITEM_SEPARATOR = ','  # Символ, який використовується для розділення елементів (слів або перекладів)
TRANSCRIPTION_SEPARATOR = '|'  # Символ, який використовується для розділення слова та транскрипції
ALLOWED_CHARS: tuple[str] = ('-', '_', ' ')  # Дозволені символи для назви словника та словникових пар

# Пагінація
VOCAB_PAGINATION_LIMIT = 10  # Кількість кнопок словників на сторінці пагінації

# Довжина назви словника
MIN_LENGTH_VOCAB_NAME = 3  # Мінімальна кількість символів у "назві словника"
MAX_LENGTH_VOCAB_NAME = 50  # Максимальна кількість символів у "назві словника"

# Довжина примітки до словника
MIN_LENGTH_VOCAB_NOTE = 3  # Мінімальна кількість символів у "примітці до словника"
MAX_LENGTH_VOCAB_NOTE = 100  # Максимальна кількість символів у "примітці до словника"

# Кількість слів у словниковій парі
MIN_COUNT_WORDS_WORDPAIR = 1  # Мінімальна кількість "слів"
MAX_COUNT_WORDS_WORDPAIR = 30  # Максимальна кількість "слів"

# Довжина слів в словниковій парі
MIN_LENGTH_WORD_WORDPAIR = 1  # Мінімальна кількість символів
MAX_LENGTH_WORD_WORDPAIR = 30  # Максимальна кількість символів

# Довжина анотації в словниковій парі
MIN_LENGTH_ANNOTATION_WORDPAIR = 1  # Мінімальна кількість символів
MAX_LENGTH_ANNOTATION_WORDPAIR = 30  # Максимальна кількість символів
