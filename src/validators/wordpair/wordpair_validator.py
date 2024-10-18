import logging

from config import (
    ALLOWED_CHARACTERS,
    MAX_LENGTH_WORD_WORDPAIR,
    MIN_LENGTH_WORD_WORDPAIR,
    TRANSCRIPTION_SEPARATOR,
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
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "Коректний формат словникової пари".')

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
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "Всі частини словникової пари не є порожніми".')

        if not self.not_empty_filter.apply(self.part_of_words):
            logging.warning('Слово словникової пари порожнє')
            self.add_validator_error('Слово словникової пари не може бути порожнім.')
            return False

        if not self.not_empty_filter.apply(self.part_of_translation):
            logging.warning('Переклад словникової пари порожній')
            self.add_validator_error('Переклад словникової пари не може бути порожнім.')
            return False
        return True

    def check_valid_transcription(self, item: str, transcription: str) -> bool:
        """Перевіряє транскрипцію"""
        if transcription is None:
            return True

        is_valid_length: bool = self.length_filter.apply(transcription)  # Чи коректна довжина
        is_valid_allowed_chars: bool = self.allowed_character_filter.apply(transcription)  # Чи коректні символи

        if not is_valid_length:
            logging.warning(f'Некоректна кількість символів у транскрипції "{transcription}" до "{item}"')
            self.add_validator_error(
                f'Довжина транскрипції до "{item}" має бути від {MIN_LENGTH_WORD_WORDPAIR} до '
                f'{MAX_LENGTH_WORD_WORDPAIR} символів')
            return False

        if not is_valid_allowed_chars:
            logging.warning(f'Некоректні символи у транскрипції: "{transcription}" до "{item}"')
            self.add_validator_error(
                f'Транскрипція може містити лише літери, цифри та символи: "{ALLOWED_CHARACTERS}".')
            return False
        return True

    def split_item_and_transcription(self, item: str) -> tuple[str, str | None]:
        """Виділяє частину словникової пари (слово або переклад) та її транскрипцію, розділені TRANSCRIPTION_SEPARATOR.
        Якщо транскрипції немає, повертається сама частина (слово або переклад) та None.
        """
        parts: list[str] = item.split(sep=TRANSCRIPTION_SEPARATOR, maxsplit=1)  # Розділений елемент
        item_only: str = parts[0].strip()  # Елемент (без зайвих пробілів)
        transcription: str | None = parts[1].strip() if len(parts) > 1 else None  # Транскрипція (якщо є)
        return item_only, transcription

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
            logging.info('ПЕРЕВІРКА СЛОВНИКОВОЇ ПАРИ НЕ БУЛА ПРОЙДЕНА. '
                        f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
            return False

        if self.check_not_empty_parts():
            logging.info('ПЕРЕВІРКА ПРОЙДЕНА: "Всі частини словникової пари не є порожніми"')
        else:
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "Всі частини словникової пари не є порожніми"')
            logging.info('ПЕРЕВІРКА СЛОВНИКОВОЇ ПАРИ НЕ БУЛА ПРОЙДЕНА. '
                        f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
            return False

        # Перевірка валідності слів
        if not WordsValidator(self.wordpair, self.vocab_name, self.errors_lst, self.validated_data).is_valid():
            logging.info('ПЕРЕВІРКА СЛОВНИКОВОЇ ПАРИ НЕ БУЛА ПРОЙДЕНА. '
                        f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
            return False

        # Перевірка валідності перекладу
        if not TranslationValidator(self.wordpair, self.vocab_name, self.errors_lst, self.validated_data).is_valid():
            logging.info('ПЕРЕВІРКА СЛОВНИКОВОЇ ПАРИ НЕ БУЛА ПРОЙДЕНА. '
                        f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
            return False

        # Перевірка валідності анотації (якщо вона є)
        if self.part_of_annotation is not None and not AnnotationValidator(self.wordpair,
                                                                           self.vocab_name,
                                                                           self.errors_lst,
                                                                           self.validated_data).is_valid():
            logging.info('ПЕРЕВІРКА СЛОВНИКОВОЇ ПАРИ НЕ БУЛА ПРОЙДЕНА. '
                        f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
            return False

        logging.info('ВСІ ПЕРЕВІРКИ СЛОВНИКОВОЇ ПАРИ УСПІШНО ПРОЙДЕНІ. '
                    f'Словникова пара: "{self.wordpair}"; Словник: "{self.vocab_name}"')
        return True
