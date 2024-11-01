import logging

from .wordpair_validator import WordPairValidator

from config import (
    ALLOWED_CHARACTERS,
    ITEM_SEPARATOR,
    MAX_COUNT_WORDS_WORDPAIR,
    MAX_LENGTH_WORD_WORDPAIR,
    MIN_COUNT_WORDS_WORDPAIR,
    MIN_LENGTH_WORD_WORDPAIR,
)
from src.filters.count_filter import CountFilter
from src.filters.valid_length_filter import LengthFilter


class TranslationValidator(WordPairValidator):
    def __init__(self, wordpair: str, vocab_name: str, errors_lst: list = None, validated_data: dict = None) -> None:
        super().__init__(wordpair, vocab_name, errors_lst)

        self.validated_data: dict = validated_data  # Коректні дані словникової пари
        self.translations_lst: list = self.part_of_translation.split(ITEM_SEPARATOR)  # Список перекладів

        # Фільтри
        self.length_filter = LengthFilter(min_length=MIN_LENGTH_WORD_WORDPAIR, max_length=MAX_LENGTH_WORD_WORDPAIR)
        self.count_filter = CountFilter(min_count=MIN_COUNT_WORDS_WORDPAIR, max_count=MAX_COUNT_WORDS_WORDPAIR)

    def check_valid_count_translations(self) -> bool:
        """Перевіряє, що коректна кількість перекладів словникової пари"""
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "Коректна кількість перекладів словникової пари"')

        count_translations: int = len(self.translations_lst)  # Кількість перекладів
        is_valid_count: bool = self.count_filter.apply(self.translations_lst)  # Чи коректна кількість

        if not is_valid_count:
            logging.warning(
                f'Кількість перекладів "{count_translations}" некоректна. '
                f'Потрібно "{MIN_COUNT_WORDS_WORDPAIR}" - "{MAX_LENGTH_WORD_WORDPAIR}"')
            self.add_validator_error(
                'Кількість перекладів до словникової пари має бути від '
                f'{MIN_COUNT_WORDS_WORDPAIR} до {MAX_COUNT_WORDS_WORDPAIR}.')
            return False
        return True

    def check_valid_all_translations(self) -> bool:
        """Перевіряє, що всі переклади словникової пари коректні"""
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "Всі переклади словникової пари коректні"')

        for translation in self.translations_lst:
            # Слово та його транскрипція
            translation, transcription = self.split_item_and_transcription(translation)

            # Чи коректний переклад та транскрипція
            is_valid_translation: bool = self._check_valid_translation(translation)
            is_valid_transcription: bool = self.check_valid_transcription(translation, transcription)

            if not is_valid_translation:
                self.validated_data['translations'].append((translation, transcription))
                return False
            if not is_valid_transcription:
                self.validated_data['translations'].append((translation, transcription))
                return False
            self.validated_data['translations'].append((translation, transcription))
        return True

    def _check_valid_translation(self, translation: str) -> bool:
        """Перевіряє переклад"""
        is_valid_length: bool = self.length_filter.apply(translation)  # Чи коректна довжина
        is_valid_allowed_chars: bool = self.allowed_character_filter.apply(translation)  # Чи коректні символи

        if not is_valid_length:
            logging.warning(f'Некоректна кількість символів у перекладі "{translation}"')
            self.add_validator_error(
                f'Довжина перекладу має бути від {MIN_LENGTH_WORD_WORDPAIR} до {MAX_LENGTH_WORD_WORDPAIR} символів.')
            return False

        # Перевірка символів у слові
        if not is_valid_allowed_chars:
            logging.warning(f'Некоректні символи у перекладі: "{translation}"')
            self.add_validator_error(f'Переклад може містити лише літери, цифри та символи: "{ALLOWED_CHARACTERS}".')
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        is_valid_flag: bool = True  # Флаг, чи коректні перевірки

        if self.check_valid_count_translations():
            logging.info('ПЕРЕВІРКА ПРОЙДЕНА: Коректна кількість перекладів словникової пари"')
        else:
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "Коректна кількість перекладів словникової пари"')
            is_valid_flag = False

        if self.check_valid_all_translations():
            logging.info('ПЕРЕВІРКА ПРОЙДЕНА: "Всі переклади словникової пари коректні"')
        else:
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "Всі переклади словникової пари коректні"')
            is_valid_flag = False

        if is_valid_flag:
            logging.info('ВСІ ПЕРЕВІРКИ ПЕРЕКЛАДІВ УСПІШНО ПРОЙДЕНІ')
        else:
            logging.info('ПЕРЕВІРКА ПЕРЕКЛАДІВ НЕ БУЛА ПРОЙДЕНА')

        return is_valid_flag
