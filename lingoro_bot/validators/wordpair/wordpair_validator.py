import logging

from lingoro_bot.config import WORDPAIR_ITEM_SEPARATOR, WORDPAIR_SEPARATOR
from lingoro_bot.text_data import MSG_ERROR_WORDPAIR_MAX_REQUIREMENT, MSG_ERROR_WORDPAIR_MIN_REQUIREMENT
from lingoro_bot.validators.base_validator import ValidatorBase
from lingoro_bot.validators.wordpair.component_validator import ComponentValidator
from lingoro_bot.validators.wordpair.item_validator import ItemValidator


class WordpairValidator(ValidatorBase):
    """Валідатор для словникової пари.

    Notes:
        Приклад (self._wordpair):
            "w1 | w_tr, w2 | w_tr2 : t | t_tr : annotation"

        Приклад (self.wordpair_parts):
            ["w1 | w_tr, w2 | w_tr2", "t | t_tr", "annotation"]
    """

    def __init__(self, wordpair: str, errors: list[str] | None = None) -> None:
        super().__init__(errors)
        self.logger: logging.Logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

        self._wordpair: str = wordpair
        self.wordpair_parts: list[str] = self._wordpair.split(WORDPAIR_SEPARATOR)

    def _check_valid_count(self) -> bool:
        """Перевіряє, чи містить словникова пара коректну кількість частин (слово, переклад, анотація)"""
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
        """Перевіряє, чи валідна анотація словникової пари.
        Якщо анотації немає (None), то вона вважається валідною.
        """
        annotation: str | None = self.wordpair_parts[2] if len(self.wordpair_parts) >= 3 else None

        # Якщо словникової пари немає (вона не обовʼязкова)
        if annotation is None:
            return True

        is_valid_annotation: bool = ComponentValidator(component=annotation, errors=self.errors).is_valid()
        return is_valid_annotation

    def _check_valid_all_words(self) -> bool:
        """Перевіряє, чи валідні всі слова словникової пари"""
        part_of_words: str = self.wordpair_parts[0]

        for item in part_of_words.split(WORDPAIR_ITEM_SEPARATOR):
            is_valid_item: bool = ItemValidator(item=item, errors=self.errors).is_valid()
            if not is_valid_item:
                return False
        return True

    def _check_valid_all_translations(self) -> bool:
        """Перевіряє, чи валідні всі переклади словникової пари.
        Перекладів може не бути (None), у цьому разі, вони вважаються не валідними.
        """
        part_of_translation: str | None = self.wordpair_parts[1] if len(self.wordpair_parts) >= 2 else None

        # Якщо перекладу немає
        if part_of_translation is None:
            return False

        for item in part_of_translation.split(WORDPAIR_ITEM_SEPARATOR):
            is_valid_item: bool = ItemValidator(item=item, errors=self.errors).is_valid()
            if not is_valid_item:
                return False
        return True

    def is_valid(self) -> bool:
        """Виконує всі перевірки для словникової пари, та повертає прапор,
        чи успішно пройдені всі перевірки.
        """
        is_valid_count_parts: bool = self._check_valid_count()
        is_valid_annotation: bool = self._check_valid_annotation()

        # Перевіряє слова та переклади лише якщо кількість частин та анотація коректна
        if is_valid_count_parts and is_valid_annotation:
            is_valid_words: bool = self._check_valid_all_words()
            is_valid_translations: bool = self._check_valid_all_translations()

            is_valid: bool = is_valid_words and is_valid_translations and is_valid_annotation
        else:
            is_valid = False

        self.logger.info(f'Словникова пара "{self._wordpair}" {"ВАЛІДНА" if is_valid else "НЕ ВАЛІДНА"}')
        return is_valid
