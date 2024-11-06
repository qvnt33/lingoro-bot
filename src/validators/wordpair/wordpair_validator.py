import logging

from config import WORDPAIR_ITEM_SEPARATOR, WORDPAIR_SEPARATOR
from src.validators.base_validator import ValidatorBase
from src.validators.wordpair.component_validator import ComponentValidator
from src.validators.wordpair.item_validator import ItemValidator
from text_data import MSG_ERROR_WORDPAIR_MAX_REQUIREMENT, MSG_ERROR_WORDPAIR_MIN_REQUIREMENT


class WordpairValidator(ValidatorBase):
    def __init__(self, wordpair: str, errors: list | None = None) -> None:
        super().__init__(errors)
        self.logger: logging.Logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

        self._wordpair: str = wordpair
        self.wordpair_parts: list[str] = self._wordpair.split(WORDPAIR_SEPARATOR)

    def _check_valid_count(self) -> bool:
        count_wordpair_parts: int = len(self.wordpair_parts)

        if count_wordpair_parts < 2:
            self.logger.warning('Словникова пара не містить слова або перекладу (частин менше 2)')
            self.add_error(MSG_ERROR_WORDPAIR_MIN_REQUIREMENT.format(separator=WORDPAIR_SEPARATOR))
            return False

        if count_wordpair_parts > 3:
            self.logger.warning('Словникова пара містить більше 3 частин')
            self.add_error(MSG_ERROR_WORDPAIR_MAX_REQUIREMENT)
            return False
        return True

    def _check_valid_annotation(self) -> bool:
        part_of_annotation: str = self.wordpair_parts[2] if len(self.wordpair_parts) >= 3 else None

        # Якщо словникової пари немає (вона не обовʼязкова)
        if part_of_annotation is None:
            return True

        is_valid_annotation: bool = ComponentValidator(component=part_of_annotation,
                                                       errors=self.errors).is_valid()
        return is_valid_annotation

    def _check_valid_all_words(self) -> bool:
        part_of_words: str = self.wordpair_parts[0]

        for item in part_of_words.split(WORDPAIR_ITEM_SEPARATOR):
            if not ItemValidator(item=item,
                                 errors=self.errors).is_valid():
                return False
        return True

    def _check_valid_all_translations(self) -> bool:
        part_of_translation: str = self.wordpair_parts[1] if len(self.wordpair_parts) >= 2 else None

        # Якщо перекладу немає
        if part_of_translation is None:
            return False

        for item in part_of_translation.split(WORDPAIR_ITEM_SEPARATOR):
            if not ItemValidator(item=item, errors=self.errors).is_valid():
                return False
        return True

    def is_valid(self) -> bool:
        self.logger.info(f'[START-VALIDATOR] Перевірка словникової пари: {self._wordpair}')

        is_valid_count_parts: bool = self._check_valid_count()
        is_valid_annotation: bool = self._check_valid_annotation()

        # Перевіряє слова та переклади лише якщо кількість частин та анотація коректна
        if is_valid_count_parts and is_valid_annotation:
            is_valid_words: bool = self._check_valid_all_words()
            is_valid_translations: bool = self._check_valid_all_translations()

            is_valid: bool = is_valid_words and is_valid_translations and is_valid_annotation
        else:
            is_valid = False

        self.logger.info(f'[END-VALIDATOR] Перевірка словникової пари: {self._wordpair}. '
                         f'Словникова пара {"ВАЛІДНА" if is_valid else "НЕ ВАЛІДНА"}')
        return is_valid
