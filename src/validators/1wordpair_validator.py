import logging
import re

from .base_validator import ValidatorBase

from config import (
    ALLOWED_CHARACTERS,
    ITEM_SEPARATOR,
    MAX_COUNT_WORDS_WORDPAIR,
    MAX_LENGTH_ANNOTATION_WORDPAIR,
    MAX_LENGTH_WORD_WORDPAIR,
    MIN_COUNT_WORDS_WORDPAIR,
    MIN_LENGTH_ANNOTATION_WORDPAIR,
    MIN_LENGTH_WORD_WORDPAIR,
    WORDPAIR_SEPARATOR,
    TRANSLITERATION_REGEX,
)
from src.filters.allowed_chars_filter import AllowedCharactersFilter
from src.filters.count_filter import CountFilter
from src.filters.length_filter import LengthFilter
from src.filters.not_empty_filters import NotEmptyFilter


class WordPairValidator(ValidatorBase):
    def __init__(self, wordpair: str, vocab_name: str, errors_lst: list = None) -> None:
        super().__init__(errors_lst)

        self.is_valid_wordpair_format = True  # Флаг, чи валідний формат словникової пари

        self.wordpair: str = wordpair.strip()  # Словникова пара без зайвих пробілів
        self.vocab_name: str = vocab_name  # Назва словника

        # Частини словникової пари
        self.wordpair_parts: list[str] = self.wordpair.split(WORDPAIR_SEPARATOR)
        self.part_of_words: str = self.wordpair_parts[0]
        self.part_of_translation: str = self.wordpair_parts[1] if len(self.wordpair_parts) >= 2 else None
        self.part_of_annotation: str = self.wordpair_parts[2] if len(self.wordpair_parts) == 3 else None

        # Фільтри
        self.allowed_character_filter = AllowedCharactersFilter(ALLOWED_CHARACTERS)
        self.not_empty_filter = NotEmptyFilter()

    def check_valid_wordpair_format(self) -> bool:
        """Перевіряє коректний формат словникової пари"""
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "коректний формат словникової пари". '
                     f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}".')

        count_parts: int = len(self.wordpair_parts)  # Кількість словникових пар

        # Якшо немає слов і переклад
        if count_parts < 2:
            self.add_validator_error('Словникова пара повинна містити щонайменше одне слово та один переклад, '
                                     f'розділені символом "{WORDPAIR_SEPARATOR}".')
            logging.warning('Словникова пара не містить перекладу')
            return False

        # Якщо словникова пара має більше 3 частин
        if count_parts > 3:
            self.add_validator_error('Максимальна кількість частин у словниковій пари - три '
                                     '(слова, переклади, анотація).')
            logging.warning('Словникова пара міє більше 3 частин')
            return False
        return True

    def check_not_empty_parts(self) -> bool:
        """Перевіряє, що всі частини словникової пари не є порожніми"""
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "всі частини словникової пари не є порожніми". '
                     f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}".')

        if not self.not_empty_filter.apply(self.part_of_words):
            logging.warning('Слово словникової пари порожнє.')
            self.add_validator_error('Слово словникової пари не може бути порожнім.')
            return False

        if not self.not_empty_filter.apply(self.part_of_translation):
            logging.warning('Переклад словникової пари порожній.')
            self.add_validator_error('Переклад словникової пари не може бути порожнім.')
            return False

        if self.not_empty_filter.apply(self.part_of_annotation):
            logging.warning('Анотація словникової пари порожня.')
            self.add_validator_error('Анотація словникової пари не може бути порожньою.')
            return False
        return True

    def extract_data(self) -> tuple | None:
        """Повертає частини словникової пари у вигляді кортежу, якщо всі вони є"""
        if self.is_valid():
            return self.part_of_words, self.part_of_translation, self.part_of_annotation
        return None

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        if not self.check_valid_wordpair_format():
            self.is_valid_wordpair_format = False
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "коректний формат словникової пари". '
                            f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
            return False
        if not self.check_not_empty_parts():
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "всі частини словникової пари не є порожніми". '
                            f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
            return False

        # Перевірка валідності слів
        if not WordsValidator(self.wordpair, self.vocab_name, self.errors_lst).is_valid():
            return False

        # Перевірка валідності перекладу
        if not TranslationValidator(self.wordpair, self.vocab_name, self.errors_lst).is_valid():
            return False

        # Перевірка валідності анотації
        if self.part_of_annotation is not None:  # noqa: SIM102
            if not AnnotationValidator(self.wordpair, self.vocab_name, self.errors_lst).is_valid():
                return False
        return True


class WordsValidator(WordPairValidator):
    def __init__(self, wordpair: str, vocab_name: str, errors_lst: list = None) -> None:
        super().__init__(wordpair, vocab_name, errors_lst)
        self.words_lst: list = self.part_of_words.split(ITEM_SEPARATOR)
        self.count_words: int = len(self.words_lst)
        self.validated_items = []

        # Фільтри
        self.length_filter = LengthFilter(min_length=MIN_LENGTH_WORD_WORDPAIR, max_length=MAX_LENGTH_WORD_WORDPAIR)
        self.count_filter = CountFilter(min_count=MIN_COUNT_WORDS_WORDPAIR, max_count=MAX_COUNT_WORDS_WORDPAIR)

    def check_valid_count_words(self) -> bool:
        """Перевіряє, що коректна кількість слів словникової пари"""
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "коректна кількість слів словникової пари". '
                     f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')

        # Має перевіряти кількість слів, а не сам список
        if not self.count_filter.apply(self.words_lst):
            logging.warning(
                f'Некоректна кількість слів у словниковій парі. '
                f'Кількість: "{self.count_words}". '
                f'Має бути: "{MIN_COUNT_WORDS_WORDPAIR}" - "{MAX_COUNT_WORDS_WORDPAIR}"')
            self.add_validator_error(
                'Кількість слів у словниковій парі має бути від '
                f'{MIN_COUNT_WORDS_WORDPAIR} до {MAX_COUNT_WORDS_WORDPAIR}.')
            return False
        return True

    def check_valid_all_words(self) -> bool:
        """Перевіряє, що всі слова словникової пари коректні"""
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "всі слова словникової пари коректні". '
                     f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
        for item in self.words_lst:
            word, transcription = self.extract_transcription_of_word(item)

            # Перевірка довжини слова
            if not self.length_filter.apply(word):
                logging.warning(f'Некоректна кількість символів у слові "{word}"')
                self.add_validator_error(
                    f'Довжина слова має бути від {MIN_LENGTH_WORD_WORDPAIR} до {MAX_LENGTH_WORD_WORDPAIR} символів.')
                return False

            # Перевірка символів у слові
            if not self.allowed_character_filter.apply(word):
                logging.warning(f'Некоректні символи у слові: "{word}". '
                                f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
                self.add_validator_error(
                    f'Слово може містити лише літери, цифри та символи: "{ALLOWED_CHARACTERS}".')
                return False

            # Перевірка транскрипції, якщо вона присутня
            if transcription is not None:
                if not self.length_filter.apply(transcription):
                    logging.warning(f'Некоректна кількість символів у транскрипції "{transcription}" до слова "{word}"')
                    self.add_validator_error(
                        f'Довжина транскрипції має бути від {MIN_LENGTH_WORD_WORDPAIR} до {MAX_LENGTH_WORD_WORDPAIR} '
                        'символів.')
                    return False

                if not self.allowed_character_filter.apply(transcription):
                    logging.warning(f'Некоректні символи у транскрипції: "{transcription}" до слова "{word}". '
                                    f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
                    self.add_validator_error(
                        f'Транскрипція може містити лише літери, цифри та символи: "{ALLOWED_CHARACTERS}".')
                    return False
        return True

    def extract_transcription_of_word(self, word: str) -> tuple[str, str | None]:
        """Виділяє слово та транскрипцію у форматі REGEX.
        Якщо транскрипції немає, повертається слово та None.
        """
        match = re.match(TRANSLITERATION_REGEX, word)
        if match:
            word_only, transcription_of_word = match.groups()
            return word_only.strip(), transcription_of_word.strip()
        return word, None

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        if not self.is_valid_wordpair_format:
            return False

        if not self.check_valid_count_words():
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "некоректна кількість слів словникової пари". '
                            f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
            return False

        if not self.check_valid_all_words():
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "всі слова словникової пари коректні". '
                            f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
            return False

        logging.warning('ПЕРЕВІРКА ПРОЙДЕНА. Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
        return True


class TranslationValidator(WordPairValidator):
    def __init__(self, wordpair: str, vocab_name: str, errors_lst: list = None) -> None:
        super().__init__(wordpair, vocab_name, errors_lst)
        self.translations_lst: list = self.part_of_translation.split(ITEM_SEPARATOR)
        self.count_translations: int = len(self.translations_lst)

        # Фільтри
        self.length_filter = LengthFilter(min_length=MIN_LENGTH_WORD_WORDPAIR, max_length=MAX_LENGTH_WORD_WORDPAIR)
        self.count_filter = CountFilter(min_count=MIN_COUNT_WORDS_WORDPAIR, max_count=MAX_COUNT_WORDS_WORDPAIR)

    def check_valid_count_translations(self) -> bool:
        """Перевіряє, що коректна кількість перекладів словникової пари"""
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "коректна кількість перекладів словникової пари". '
                     f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')

        if not self.count_filter.apply(self.translations_lst):
            logging.warning(
                f'Некоректна кількість перекладів словникової пари. '
                f'Кількість: "{self.count_translations}". '
                f'Має бути: "{MIN_COUNT_WORDS_WORDPAIR}" - "{MAX_COUNT_WORDS_WORDPAIR}"')
            self.add_validator_error(
                'Кількість перекладів до словникової пари має бути від '
                f'{MIN_COUNT_WORDS_WORDPAIR} до {MAX_COUNT_WORDS_WORDPAIR}.')
            return False

        logging.info('ПЕРЕВІРКА УСПІШНО ПРОЙДЕНА: коректна кількість перекладів словникової пари. '
                     f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
        return True

    def check_valid_all_translations(self) -> bool:
        """Перевіряє, що всі переклади словникової пари коректні"""
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "всі переклади словникової пари коректні". '
                     f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')

        for translation in self.translations_lst:
            if not self.length_filter.apply(translation):
                logging.warning(f'Некоректна кількість символів у перекладів "{translation}"')
                self.add_validator_error(
                    'Довжина перекладу має бути від '
                    f'{MIN_LENGTH_WORD_WORDPAIR} до {MAX_LENGTH_WORD_WORDPAIR} символів.')
                return False

            if not self.allowed_character_filter.apply(translation):
                logging.warning(f'Некоректні символи у перекладі: "{translation}"')
                self.add_validator_error(
                    f'Переклад до словникової пари може містити лише літери, цифри та символи: "{ALLOWED_CHARACTERS}".')
                return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        # Якщо некоректний формат у словниковій парі
        if not self.is_valid_wordpair_format:
            return False

        if not self.check_valid_count_translations():
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "коректна кількість перекладів словникової пари". '
                            f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
            return False
        if not self.check_valid_all_translations():
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "всі переклади словникової пари коректні". '
                            f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
            return False
        return True


class AnnotationValidator(WordPairValidator):
    def __init__(self, wordpair: str, vocab_name: str, errors_lst: list = None) -> None:
        super().__init__(wordpair, vocab_name, errors_lst)
        self.annotation: list = self.part_of_annotation.strip() if self.part_of_annotation else None

        # Фільтри
        self.length_filter = LengthFilter(min_length=MIN_LENGTH_ANNOTATION_WORDPAIR,
                                          max_length=MAX_LENGTH_ANNOTATION_WORDPAIR)

    def check_valid_length_annotation(self) -> bool:
        """Перевіряє, що коректна кількість символів у анотації"""
        # Якщо анотації немає
        if self.annotation is None:
            return False

        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "кількість символів у анотації коректна". '
                     f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')

        if not self.length_filter.apply(self.annotation):
            logging.warning(f'Некоректна кількість символів у анотації "{self.annotation}"')
            self.add_validator_error(
                f'Довжина анотації має бути від {MIN_LENGTH_WORD_WORDPAIR} до {MAX_LENGTH_WORD_WORDPAIR} символів.')
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        # Якщо некоректний формат у словниковій парі
        if not self.is_valid_wordpair_format:
            return False

        if self.annotation is None:
            return False

        if not self.check_valid_length_annotation():
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "кількість символів у анотації коректна". '
                            f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
            return False
        return True
