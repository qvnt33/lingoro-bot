import logging

from .wordpair_validator import WordPairValidator

from config import (
    ALLOWED_CHARACTERS,
    ITEM_SEPARATOR,
    MAX_COUNT_WORDS_WORDPAIR,
    MAX_LENGTH_WORD_WORDPAIR,
    MIN_COUNT_WORDS_WORDPAIR,
    MIN_LENGTH_WORD_WORDPAIR,
    TRANSCRIPTION_SEPARATOR,
)
from src.filters.count_filter import CountFilter
from src.filters.length_filter import LengthFilter


class WordsValidator(WordPairValidator):
    def __init__(self, wordpair: str, vocab_name: str, errors_lst: list = None, validated_data: dict = None) -> None:
        super().__init__(wordpair, vocab_name, errors_lst)

        self.validated_data: dict = validated_data  # Коректні дані словникової пари
        self.words_lst: list = self.part_of_words.split(ITEM_SEPARATOR)  # Список слів словникової пари

        # Фільтри
        self.length_filter = LengthFilter(min_length=MIN_LENGTH_WORD_WORDPAIR, max_length=MAX_LENGTH_WORD_WORDPAIR)
        self.count_filter = CountFilter(min_count=MIN_COUNT_WORDS_WORDPAIR, max_count=MAX_COUNT_WORDS_WORDPAIR)

    def check_valid_count_words(self) -> bool:
        """Перевіряє, що коректна кількість слів словникової пари"""
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "Коректна кількість слів словникової пари". '
                     f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')

        count_words: int = len(self.words_lst)  # Кількість слів
        is_valid_count: bool = self.count_filter.apply(self.words_lst)  # Чи коректна кількість

        if not is_valid_count:
            logging.warning(
                f'Кількість слів "{count_words}" некоректна. '
                f'Потрібно "{MIN_COUNT_WORDS_WORDPAIR}" - "{MAX_LENGTH_WORD_WORDPAIR}"')
            self.add_validator_error(
                'Кількість слів до словникової пари має бути від '
                f'{MIN_COUNT_WORDS_WORDPAIR} до {MAX_COUNT_WORDS_WORDPAIR}.')
            return False
        return True

    def check_valid_all_words(self) -> bool:
        """Перевіряє, що всі слова словникової пари коректні"""
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "Всі слова словникової пари коректні"')

        for word in self.words_lst:
            # Слово та його транскрипція
            word, transcription = self._split_word_and_transcription(word)

            # Чи валідне слово та транскрипція
            is_valid_word: bool = self._check_valid_word(word)
            is_valid_transcription: bool = self._check_valid_transcription(word, transcription)

            if not is_valid_word:
                self.validated_data['words'].append((word, transcription))  # Додавання до валідної бази слово
                return False
            if not is_valid_transcription:
                self.validated_data['words'].append((word, transcription))  # Додавання до валідної бази слово
                return False
            self.validated_data['words'].append((word, transcription))  # Додавання до валідної бази слово
        return True

    def _check_valid_word(self, word: str) -> bool:
        """Перевіряє слово"""
        is_valid_length: bool = self.length_filter.apply(word)  # Чи коректна довжина
        is_valid_allowed_chars: bool = self.allowed_character_filter.apply(word)  # Чи коректні символи

        if not is_valid_length:
            logging.warning(f'Некоректна кількість символів у слові "{word}"')
            self.add_validator_error(
                f'Довжина слова має бути від {MIN_LENGTH_WORD_WORDPAIR} до {MAX_LENGTH_WORD_WORDPAIR} символів.')
            return False

        # Перевірка символів у слові
        if not is_valid_allowed_chars:
            logging.warning(f'Некоректні символи у слові: "{word}"')
            self.add_validator_error(f'Слово може містити лише літери, цифри та символи: "{ALLOWED_CHARACTERS}".')
            return False
        return True

    def _check_valid_transcription(self, word: str, transcription: str) -> bool:
        """Перевіряє транскрипцію"""
        if transcription is None:
            return True

        is_valid_length: bool = self.length_filter.apply(transcription)  # Чи коректна довжина
        is_valid_allowed_chars: bool = self.allowed_character_filter.apply(transcription)  # Чи коректні символи

        if not is_valid_length:
            logging.warning(f'Некоректна кількість символів у транскрипції "{transcription}" до слова "{word}"')
            self.add_validator_error(
                f'Довжина транскрипції до слова "{word}" має бути від {MIN_LENGTH_WORD_WORDPAIR} до '
                f'{MAX_LENGTH_WORD_WORDPAIR} символів')
            return False

        if not is_valid_allowed_chars:
            logging.warning(f'Некоректні символи у транскрипції: "{transcription}" до слова "{word}"')
            self.add_validator_error(
                f'Транскрипція може містити лише літери, цифри та символи: "{ALLOWED_CHARACTERS}".')
            return False
        return True

    def _split_word_and_transcription(self, word: str) -> tuple[str, str | None]:
        """Виділяє слово та транскрипцію у форматі REGEX.
        Якщо транскрипції немає, повертається слово та None
        """
        parts: list[str] = word.split(sep=TRANSCRIPTION_SEPARATOR, maxsplit=1)  # Розділене слово
        word_only: str = parts[0].strip()  # Слово (без зайвих пробілів)
        transcription: str | None = parts[1].strip() if len(parts) > 1 else None  # Транскрипція (якщо є)
        return word_only, transcription

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        is_valid_flag: bool = True  # Флаг, чи коректні перевірки

        if self.check_valid_count_words():
            logging.info('ПЕРЕВІРКА ПРОЙДЕНА: "Некоректна кількість слів словникової пари"')
        else:
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "Некоректна кількість слів словникової пари"')
            is_valid_flag = False

        if self.check_valid_all_words():
            logging.info('ПЕРЕВІРКА ПРОЙДЕНА: "Всі слова словникової пари коректні"')
        else:
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "Всі слова словникової пари коректні"')
            is_valid_flag = False

        if is_valid_flag:
            logging.info('ВСІ ПЕРЕВІРКИ СЛІВ ПАРИ УСПІШНО ПРОЙДЕНІ')
        else:
            logging.info('ПЕРЕВІРКА СЛІВ НЕ БУЛА ПРОЙДЕНА')
        return is_valid_flag
