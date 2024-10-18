import logging

from .wordpair_validator import WordPairValidator

from config import (
    MAX_LENGTH_ANNOTATION_WORDPAIR,
    MAX_LENGTH_WORD_WORDPAIR,
    MIN_LENGTH_ANNOTATION_WORDPAIR,
    MIN_LENGTH_WORD_WORDPAIR,
)
from src.filters.length_filter import LengthFilter


class AnnotationValidator(WordPairValidator):
    def __init__(self, wordpair: str, vocab_name: str, errors_lst: list = None, validated_data: dict = None) -> None:
        super().__init__(wordpair, vocab_name, errors_lst)

        self.validated_data = validated_data  # Коректні дані словникової пари

        self.annotation: list = self.part_of_annotation.strip()  # Анотація (без зайвих пробілів)

        # Фільтри
        self.length_filter = LengthFilter(min_length=MIN_LENGTH_ANNOTATION_WORDPAIR,
                                          max_length=MAX_LENGTH_ANNOTATION_WORDPAIR)

    def check_valid_length_annotation(self) -> bool:
        """Перевіряє, що коректна кількість символів у анотації"""
        logging.info('ПОЧАТОК ПЕРЕВІРКИ: "Кількість символів у анотації коректна".')

        length_annotation: int = len(self.annotation)  # Довжина анотації
        is_valid_length: bool = self.length_filter.apply(self.annotation)  # Чи коректна довжина

        if not is_valid_length:
            logging.warning(
                f'Кількість символів "{length_annotation}" некоректна. '
                f'Потрібно "{MIN_LENGTH_WORD_WORDPAIR}" - "{MAX_LENGTH_WORD_WORDPAIR}"')
            self.add_validator_error(
                f'Довжина анотації має бути від {MIN_LENGTH_WORD_WORDPAIR} до {MAX_LENGTH_WORD_WORDPAIR} символів.')
            return False
        return True

    def is_valid(self) -> bool:
        """Запускає всі перевірки і повертає True, якщо всі вони пройдені"""
        is_valid_flag = True

        if self.check_valid_length_annotation():
            logging.info('ПЕРЕВІРКА ПРОЙДЕНА: "Кількість символів у анотації коректна"')
        else:
            logging.warning('ПЕРЕВІРКА НЕ ПРОЙДЕНА: "Кількість символів у анотації коректна"')
            is_valid_flag = False

        if is_valid_flag:
            logging.info('ВСІ ПЕРЕВІРКИ АНОТАЦІЇ УСПІШНО ПРОЙДЕНІ')
        else:
            logging.info('ПЕРЕВІРКА АНОТАЦІЇ НЕ БУЛА ПРОЙДЕНА')

        self.validated_data['annotation'] = self.annotation  # Додавання до бази валідної анотації
        logging.info(f'Анотація "{self.annotation}" була додана до валідної бази')

        return is_valid_flag
