import logging

from config import (
    ALLOWED_CHARACTERS,
    WORDPAIR_SEPARATOR,
)
from src.filters.allowed_chars_filter import AllowedCharactersFilter
from src.filters.not_empty_filters import NotEmptyFilter
from src.validators.base_validator import ValidatorBase


class WordPairValidator(ValidatorBase):
    def __init__(self, wordpair: str, vocab_name: str, errors_lst: list = None) -> None:
        super().__init__(errors_lst)

        self.wordpair: str = wordpair.strip()  # Словникова пара без зайвих пробілів
        self.vocab_name: str = vocab_name  # Назва словника
        # Коректні дані словникової пари
        self.validated_data: list = {'words': [], 'translations': [], 'annotation': ''}

        # Частини словникової пари
        self.wordpair_parts: list[str] = self.wordpair.split(WORDPAIR_SEPARATOR)
        self.part_of_words: str = self.wordpair_parts[0]
        self.part_of_translation: str = self.wordpair_parts[1] if len(self.wordpair_parts) >= 2 else None
        self.part_of_annotation: str = self.wordpair_parts[2] if len(self.wordpair_parts) == 3 else None

        # Фільтри
        self.allowed_character_filter = AllowedCharactersFilter(ALLOWED_CHARACTERS)
        self.not_empty_filter = NotEmptyFilter()

    def check_valid_wordpair_format(self) -> bool:
        """Перевіряє, що коректний формат словникової пари"""
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "Коректний формат словникової пари". '
                     f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}".')

        count_parts: int = len(self.wordpair_parts)  # Кількість словникових пар

        # Якшо немає слова та перекладу
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
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "Всі частини словникової пари не є порожніми". '
                     f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}".')

        if not self.not_empty_filter.apply(self.part_of_words):
            logging.warning('Слово словникової пари порожнє')
            self.add_validator_error('Слово словникової пари не може бути порожнім.')
            return False

        if not self.not_empty_filter.apply(self.part_of_translation):
            logging.warning('Переклад словникової пари порожній')
            self.add_validator_error('Переклад словникової пари не може бути порожнім.')
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        logging.info('ПОЧАТОК ВСІХ ПЕРЕВІРОК СЛОВНИКОВОЇ ПАРИ. '
                     f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')

        from .annotation_validator import AnnotationValidator
        from .translation_validator import TranslationValidator
        from .word_validator import WordsValidator

        if self.check_valid_wordpair_format():
            logging.info('ПЕРЕВІРКА ПРОЙДЕНА: "Коректний формат словникової пари"')
        else:
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "Коректний формат словникової пари"')
            return False

        if self.check_not_empty_parts():
            logging.info('ПЕРЕВІРКА ПРОЙДЕНА: "Всі частини словникової пари не є порожніми"')
        else:
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "Всі частини словникової пари не є порожніми"')
            return False

        # Перевірка валідності слів
        if not WordsValidator(self.wordpair, self.vocab_name, self.errors_lst, self.validated_data).is_valid():
            return False

        # Перевірка валідності перекладу
        if not TranslationValidator(self.wordpair, self.vocab_name, self.errors_lst, self.validated_data).is_valid():
            return False

        # Перевірка валідності анотації (якщо вона є)
        if self.part_of_annotation is not None and not AnnotationValidator(self.wordpair,
                                                                           self.vocab_name,
                                                                           self.errors_lst,
                                                                           self.validated_data).is_valid():
            return False

        logging.info('ПЕРЕВІРКА СЛОВНИКОВОЇ ПАРИ УСПІШНО ПРОЙДЕНА. '
                     f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')

        return True
