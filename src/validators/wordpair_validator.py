from .base_validator import ValidatorBase

from config import (
    ALLOWED_CHARACTERS,
    ITEM_SEPARATOR,
    MAX_COUNT_TRANSLATIONS_WORDPAIR,
    MAX_COUNT_WORDS_WORDPAIR,
    MAX_LENGTH_ANNOTATION_WORDPAIR,
    MAX_LENGTH_TRANSLATION_WORDPAIR,
    MAX_LENGTH_WORD_WORDPAIR,
    MIN_COUNT_TRANSLATIONS_WORDPAIR,
    MIN_COUNT_WORDS_WORDPAIR,
    MIN_LENGTH_ANNOTATION_WORDPAIR,
    MIN_LENGTH_TRANSLATION_WORDPAIR,
    MIN_LENGTH_WORD_WORDPAIR,
    WORDPAIR_SEPARATOR,
)
from src.filters.count_filter import CountFilter
from src.filters.length_filter import LengthFilter


class WordPairValidator(ValidatorBase):
    def __init__(self, wordpair: str) -> None:
        super().__init__()
        self.wordpair: str = wordpair.strip()  # Словникова пара (без зайвих пробілів)
        self.wordpair_parts: list[str] = self.wordpair.split(WORDPAIR_SEPARATOR)  # Частини словникової пари

        # Частини словникової пари
        self.part_of_words: str = self.wordpair_parts[0]
        self.part_of_translation: str = self.wordpair_parts[1] if len(self.wordpair_parts) >= 2 else None
        self.part_of_annotation: str = self.wordpair_parts[2] if len(self.wordpair_parts) == 3 else None

    def check_valid_format(self) -> bool:
        """Перевіряє, що коректний формат словникової пари"""
        count_parts: int = len(self.wordpair_parts)  # Кількість частин словникової пари

        # Перевірка на наявність хоча б 2 частин (слово і переклад)
        if count_parts < 2:
            error_text: str = (
                'Словникова пара повинна містити щонайменше одне слово та один переклад, '
                f'розділені символом "{WORDPAIR_SEPARATOR}".')
            log_text: str = f'Словникова пара "{self.wordpair}" до словника "{self.name}" не містить перекладу.'
            self.add_error_with_log(error_text, log_text)  # Додавання помилок та виведення логування
            return False

        # Перевірка на наявність не більше ніж 3 частини (слова, переклади, анотація)
        if count_parts > 3:
            error_text: str = 'Максимальна кількість частин у словниковій парі - три (слова, переклади, анотація).'
            log_text: str = f'Словникова пара "{self.wordpair}" до словника "{self.name}" має більше 3 частин.'
            self.add_error_with_log(error_text, log_text)  # Додавання помилок та виведення логування
            return False

        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        return self.check_valid_format()


class WordsValidator(WordPairValidator):
    def __init__(self, wordpair: str) -> None:
        super().__init__(wordpair)
        self.words_lst: list = self.part_of_words.split(ITEM_SEPARATOR)  # Список слів
        self.count_words: int = len(self.words_lst)  # Кількість слів

        # Фільтри
        self.length_filter = LengthFilter(min_length=MIN_LENGTH_WORD_WORDPAIR, max_length=MAX_LENGTH_WORD_WORDPAIR)
        self.count_filter = CountFilter(min_count=MIN_COUNT_WORDS_WORDPAIR, max_count=MAX_COUNT_WORDS_WORDPAIR)

    def check_valid_count(self) -> bool:
        """Перевіряє, що коректна кількість всіх слів у словниковій парі"""
        if not self.count_filter.apply(self.count_words):
            error_text: str = (
                    'Кількість слів до словникової має бути від '
                    f'{MIN_COUNT_WORDS_WORDPAIR} до {MAX_COUNT_WORDS_WORDPAIR} слів.')
            log_text: str = (
                f'Словникова пара "{self.wordpair}" не відповідає вимогам по кількості СЛІВ. '
                f'Кількість: "{self.count_words}". '
                f'Має бути: "{MIN_COUNT_WORDS_WORDPAIR}" - "{MAX_COUNT_WORDS_WORDPAIR}"')
            self.add_error_with_log(error_text, log_text)
            return False
        return True

    def check_valid_all_items(self) -> bool:
        """Перевіряє, що кожне слово в словниковій парі відповідає вимогам"""
        for word in self.words_lst:
            if not self.length_filter.apply(len(word)):
                error_text: str = (
                    'Кількість слів до словникової має бути від '
                    f'{MIN_COUNT_WORDS_WORDPAIR} до {MAX_COUNT_WORDS_WORDPAIR} слів.')
                log_text: str = (
                    f'Словникова пара "{self.wordpair}" не відповідає вимогам по кількості СЛІВ. '
                    f'Кількість: "{self.count_words}". '
                    f'Має бути: "{MIN_COUNT_WORDS_WORDPAIR}" - "{MAX_COUNT_WORDS_WORDPAIR}"')
                self.add_error_with_log(error_text, log_text)
                return False

            if not self.allowed_character_filter.apply(word):
                error_text = f'Слово "{word}" може містити лише літери, цифри та символи "{ALLOWED_CHARACTERS}".'
                log_text = f'Слово "{word}" містить некоректні символи.'
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
        # Список перекладів
        self.translations_lst: list = self.part_of_translation.split(ITEM_SEPARATOR) if self.part_of_translation else []
        self.count_translations: int = len(self.translations_lst)  # Кількість перекладів

        # Фільтри
        self.count_filter = CountFilter(min_count=MIN_COUNT_TRANSLATIONS_WORDPAIR,
                                        max_count=MAX_COUNT_TRANSLATIONS_WORDPAIR)
        self.length_filter = LengthFilter(min_length=MIN_LENGTH_TRANSLATION_WORDPAIR,
                                          max_length=MAX_LENGTH_TRANSLATION_WORDPAIR)

    def check_valid_count(self) -> bool:
        """Перевіряє кількість перекладів"""
        if not self.count_filter.apply(self.count_translations):
            error_text: str = (
                'Кількість перекладів до словникової має бути від '
                f'{MIN_COUNT_TRANSLATIONS_WORDPAIR} до {MAX_COUNT_TRANSLATIONS_WORDPAIR} перекладів.')
            log_text: str = (
                f'Словникова пара "{self.wordpair}" не відповідає вимогам по кількості ПЕРЕКЛАДІВ. '
                f'Кількість: "{self.count_translations}". '
                f'Має бути: "{MIN_COUNT_TRANSLATIONS_WORDPAIR}" - "{MAX_COUNT_TRANSLATIONS_WORDPAIR}"')
            self.add_error_with_log(error_text, log_text)
            return False
        return True

    def check_valid_all_items(self) -> bool:
        """Перевіряє кожен переклад"""
        for translation in self.translations_lst:
            if not self.length_filter.apply(len(translation)):
                error_text: str = (
                'Кількість перекладів до словникової має бути від '
                f'{MIN_COUNT_TRANSLATIONS_WORDPAIR} до {MAX_COUNT_TRANSLATIONS_WORDPAIR} перекладів.')
                log_text: str = (
                    f'Словникова пара "{self.wordpair}" не відповідає вимогам по кількості ПЕРЕКЛАДІВ. '
                    f'Кількість: "{self.count_translations}". '
                    f'Має бути: "{MIN_COUNT_TRANSLATIONS_WORDPAIR}" - "{MAX_COUNT_TRANSLATIONS_WORDPAIR}"')
                self.add_error_with_log(error_text, log_text)
                return False

            if not self.allowed_character_filter.apply(translation):
                error_text: str = (
                    f'Переклад до словникової пари може містити лише літери, цифри та символи: "{ALLOWED_CHARACTERS}".')
                log_text: str = (
                    f'Переклад "{translation}" до словникової пари "{self.name}" містить некоректні символи. '
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

        self.length_filter = LengthFilter(min_length=MIN_LENGTH_TRANSLATION_WORDPAIR,
                                          max_length=MAX_LENGTH_TRANSLATION_WORDPAIR)
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
