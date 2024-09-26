import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

TOKEN = os.getenv('TOKEN')
VOCAB_PAGINATION_LIMIT = 10  # Ліміт кількості кнопок словників на сторінці пагінації
MIN_LENGTH_VOCAB_NAME = 3
MAX_LENGTH_VOCAB_NAME = 50
