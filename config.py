import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

TOKEN = os.getenv('TOKEN')
VOCAB_PAGINATION_LIMIT = 10  # Ліміт кількості кнопок словників на сторінці пагінації

MIN_LENGTH_VOCAB_NAME = 3
MAX_LENGTH_VOCAB_NAME = 50

MIN_LENGTH_VOCAB_NOTE = 3
MAX_LENGTH_VOCAB_NOTE = 100

DEFAULT_VOCAB_NOTE = 'Немає'

MAX_COUNT_WORDS_WORDPAIR = 3
MAX_COUNT_TRANSLATIONS_WORDPAIR = 3
MAX_LENGTH_WORD_WORDPAIR = 30
MAX_LENGTH_TRANSLATION_WORDPAIR = 30
