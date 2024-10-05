import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

TOKEN = os.getenv('TOKEN')  # Токен Телеграм

DEFAULT_VOCAB_NOTE = 'Немає'  # Стандартна назва примітки до словника
WORDPAIR_SEPARATOR = ':'  # Символ, за допомогою якого будуть розділяти словникові пари

VOCAB_PAGINATION_LIMIT = 10  # Кількість кнопок словників на сторінці пагінації

MIN_LENGTH_VOCAB_NAME = 3  # Мінімальна к-сть символів у "назві" словника
MAX_LENGTH_VOCAB_NAME = 50  # Максимальна к-сть символів у "назві" словника

MIN_LENGTH_VOCAB_NOTE = 3  # Мінімальна кількість символів у "примітці" до словника
MAX_LENGTH_VOCAB_NOTE = 100  # Максимальна кількість символів у "примітці" до словника

MIN_COUNT_WORDS_WORDPAIR = 1  # Мінімальна кількість "слів" у словниковій парі
MAX_COUNT_WORDS_WORDPAIR = 3  # Максимальна кількість "слів" у словниковій парі

MIN_COUNT_TRANSLATIONS_WORDPAIR = 1  # Мінімальна кількість "перекладів" у словниковій парі
MAX_COUNT_TRANSLATIONS_WORDPAIR = 3  # Максимальна кількість "перекладів" у словниковій парі

MIN_LENGTH_WORD_WORDPAIR = 1  # Мінімальна кількість "слів" у одній словниковій парі
MAX_LENGTH_WORD_WORDPAIR = 30  # Максимальна кількість "слів" у одній словниковій парі

MIN_LENGTH_TRANSLATION_WORDPAIR = 1  # Мінімальна кількість "перекладів" у одній словниковій парі
MAX_LENGTH_TRANSLATION_WORDPAIR = 30  # Максимальна кількість "перекладів" у одній словниковій парі
