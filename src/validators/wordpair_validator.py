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
)
from src.filters.allowed_chars_filter import AllowedCharactersFilter
from src.filters.count_filter import CountFilter
from src.filters.length_filter import LengthFilter
from src.filters.not_empty_filters import NotEmptyFilter


class WordPairValidator(ValidatorBase):
    def __init__(self, wordpair: str, vocab_name: str) -> None:
        super().__init__()
        self.wordpair: str = wordpair.strip()  # Словникова пара (без зайвих пробілів)
        self.vocab_name: str = vocab_name  # Назва словника

        # Частини словникової пари
        self.wordpair_parts: list[str] = self.wordpair.split(WORDPAIR_SEPARATOR)
        self.part_of_words: str = self.wordpair_parts[0]
        self.part_of_translation: str = self.wordpair_parts[1] if len(self.wordpair_parts) >= 2 else None
        self.part_of_annotation: str = self.wordpair_parts[2] if len(self.wordpair_parts) == 3 else None

        self.valid_wordpairs: list[str] = []  # Список валідних словникових пар

        # Фільтри
        self.length_filter = LengthFilter(min_length=MIN_LENGTH_WORD_WORDPAIR, max_length=MAX_LENGTH_WORD_WORDPAIR)
        self.count_filter = CountFilter(min_count=MIN_COUNT_WORDS_WORDPAIR, max_count=MAX_COUNT_WORDS_WORDPAIR)
        self.allowed_character_filter = AllowedCharactersFilter(allowed_characters=ALLOWED_CHARACTERS)
        self.not_empty_filter = NotEmptyFilter()

    def check_valid_format(self) -> bool:
        """Перевіряє, що коректний формат словникової пари"""
        count_parts: int = len(self.wordpair_parts)  # Кількість частин словникової пари

        # Перевірка на наявність хоча б 2 частин (слово і переклад)
        if count_parts < 2:
            error_text: str = (
                'Словникова пара повинна містити щонайменше одне слово та один переклад, '
                f'розділені символом "{WORDPAIR_SEPARATOR}".')
            log_text: str = f'Словникова пара "{self.wordpair}" до словника "{self.vocab_name}" не містить перекладу.'
            self.add_error_with_log(error_text, log_text)  # Додавання помилок та виведення логування
            return False

        # Перевірка на наявність не більше ніж 3 частини (слова, переклади, анотація)
        if count_parts > 3:
            error_text: str = 'Максимальна кількість частин у словниковій парі - три (слова, переклади, анотація).'
            log_text: str = f'Словникова пара "{self.wordpair}" до словника "{self.vocab_name}" має більше 3 частин.'
            self.add_error_with_log(error_text, log_text)
            return False
        return True

    def check_not_empty_parts(self) -> bool:
        # Перевірка, що кожна частина не є порожньою
        if not self.not_empty_filter.apply(self.part_of_words):
            error_text: str = 'Слово в словниковій парі не може бути порожнім.'
            log_text: str = f'Слово в словниковій парі "{self.wordpair}" порожнє.'
            self.add_error_with_log(error_text, log_text)
            return False

        if not self.not_empty_filter.apply(self.part_of_translation):
            error_text: str = 'Переклад в словниковій парі не може бути порожнім.'
            log_text: SystemError = f'Переклад у словниковій парі "{self.wordpair}" порожній.'
            self.add_error_with_log(error_text, log_text)
            return False

        # Якщо є анотація, перевіряємо, що вона теж не порожня (якщо фільтр приймає None - то повертає True)
        if not self.not_empty_filter.apply(self.part_of_annotation):
            error_text: str = 'Анотація в словниковій парі не може бути порожньою, якщо вона присутня.'
            log_text: str = f'Анотація в словниковій парі "{self.wordpair}" порожня.'
            self.add_error_with_log(error_text, log_text)
            return False
        return True

    def extract_data(self) -> tuple:
        """Повертає валідні словникові пари у вигляді кортежу:
        (слова, переклади, анотація або None)
        """
        if self.is_valid():
            return (self.part_of_words, self.part_of_translation, self.part_of_annotation)
        return None

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        if not self.check_valid_format():
            return False

        checks: list[bool] = [self.check_not_empty_parts()]
        return all(checks)


class WordsValidator(WordPairValidator):
    def __init__(self, wordpair: str) -> None:
        super().__init__(wordpair)
        self.words_lst: list = self.part_of_words.split(ITEM_SEPARATOR)
        self.count_words: int = len(self.words_lst)

    def check_valid_count(self) -> bool:
        """Перевіряє, що коректна кількість"""
        if not self.count_filter.apply(self.count_words):
            error_text: str = (
                'Кількість слів до словникової пари має бути від '
                f'{MIN_COUNT_WORDS_WORDPAIR} до {MAX_COUNT_WORDS_WORDPAIR}.')
            log_text: str = (
                f'Словникова пара "{self.wordpair}" не відповідає вимогам по кількості слів. '
                f'Кількість: "{self.count_words}". '
                f'Має бути: "{MIN_COUNT_WORDS_WORDPAIR}" - "{MAX_COUNT_WORDS_WORDPAIR}"')
            self.add_error_with_log(error_text, log_text)
            return False
        return True

    def check_valid_all_items(self) -> bool:
        """Перевіряє, що кожне слово словникової пари відповідає вимогам"""
        for word in self.words_lst:
            length_word: int = len(word)

            if not self.length_filter.apply(word):
                error_text: str = (
                    f'Слово до словникової пари має містити від {MIN_LENGTH_WORD_WORDPAIR} до '
                    f'{MAX_LENGTH_WORD_WORDPAIR} символів.')
                log_text: str = (
                    f'Слово "{word}" до словникової пари "{self.wordpair}" не відповідає вимогам по довжині.'
                    f'Довжина: "{length_word}". '
                    f'Має бути: "{MIN_LENGTH_WORD_WORDPAIR}" - "{MAX_LENGTH_WORD_WORDPAIR}"')
                self.add_error_with_log(error_text, log_text)
                return False

            if not self.allowed_character_filter.apply(word):
                error_text: str = (
                    f'Слово до словникової пари може містити лише літери, цифри та символи: "{ALLOWED_CHARACTERS}".')
                log_text: str = (
                    f'Слово "{word}" до словникової пари "{self.wordpair}" містить некоректні символи. '
                    f'Допустимі символи: літери, цифри та "{ALLOWED_CHARACTERS}"')
                self.add_error_with_log(error_text, log_text)
                return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        if not self.check_valid_format():
            return False

        checks: list[bool] = [self.check_valid_count(),
                              self.check_valid_all_items()]
        return all(checks)


class TranslationValidator(WordPairValidator):
    def __init__(self, wordpair: str) -> None:
        super().__init__(wordpair)
        self.translations_lst: list = self.part_of_translation.split(ITEM_SEPARATOR) if self.part_of_translation else []
        self.count_translations: int = len(self.translations_lst)

    def check_valid_count(self) -> bool:
        """Перевіряє, що коректна кількість"""
        if not self.count_filter.apply(self.count_translations):
            error_text: str = (
                'Кількість перекладів до словникової пари має бути від '
                f'{MIN_COUNT_WORDS_WORDPAIR} до {MAX_COUNT_WORDS_WORDPAIR}.')
            log_text: str = (
                f'Словникова пара "{self.wordpair}" не відповідає вимогам по кількості перекладів. '
                f'Кількість: "{self.count_words}". '
                f'Має бути: "{MIN_COUNT_WORDS_WORDPAIR}" - "{MAX_COUNT_WORDS_WORDPAIR}"')
            self.add_error_with_log(error_text, log_text)
            return False
        return True

    def check_valid_all_items(self) -> bool:
        """Перевіряє, що кожен переклад словникової пари відповідає вимогам"""
        for translation in self.translations_lst:
            length_translation: int = len(translation)

            if not self.length_filter.apply(translation):
                error_text: str = (
                    f'Переклад до словникової пари має містити від {MIN_LENGTH_WORD_WORDPAIR} до '
                    f'{MAX_LENGTH_WORD_WORDPAIR} символів.')
                log_text: str = (
                    f'Переклад "{translation}" до словникової пари "{self.wordpair}" не відповідає вимогам по довжині.'
                    f'Довжина: "{length_translation}". '
                    f'Має бути: "{MIN_LENGTH_WORD_WORDPAIR}" - "{MAX_LENGTH_WORD_WORDPAIR}"')
                self.add_error_with_log(error_text, log_text)
                return False

            if not self.allowed_character_filter.apply(translation):
                error_text: str = (
                    f'Переклад до словникової пари може містити лише літери, цифри та символи: "{ALLOWED_CHARACTERS}".')
                log_text: str = (
                    f'Переклад "{translation}" до словникової пари "{self.wordpair}" містить некоректні символи. '
                    f'Допустимі символи: літери, цифри та "{ALLOWED_CHARACTERS}"')
                self.add_error_with_log(error_text, log_text)
                return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        if not self.check_valid_format():
            return False

        checks: list[bool] = [self.check_valid_count(), self.check_valid_all_items()]
        return all(checks)


class AnnotationValidator(WordPairValidator):
    def __init__(self, wordpair: str) -> None:
        super().__init__(wordpair)

        self.annotation: list = self.part_of_annotation.strip() if self.part_of_annotation else None

    def check_valid_length(self) -> bool:
        """Перевіряє, що коректна кількість символів у анотації"""
        if self.annotation is None:
            return False

        self.length_filter = LengthFilter(min_length=MIN_LENGTH_ANNOTATION_WORDPAIR,
                                          max_length=MAX_LENGTH_ANNOTATION_WORDPAIR)
        length_annotation: int = len(self.annotation)

        if not self.length_filter(value=length_annotation):
            error_text: str = (
                f'Анотація до словникової пари має містити від {MIN_LENGTH_ANNOTATION_WORDPAIR} до '
                f'{MAX_LENGTH_ANNOTATION_WORDPAIR} символів.')
            log_text: str = (
                f'Анотація "{self.annotation_of_wordpair}" до словникової пари "{self.wordpair}" не '
                f'відповідає вимогам по довжині. Кількість символів: "{length_annotation}".')
            self.add_error_with_log(error_text, log_text)
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        if self.annotation is None:
            return False

        checks: list[bool] = [self.check_valid_length()]
        return all(checks)
