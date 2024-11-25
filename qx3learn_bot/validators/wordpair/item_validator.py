
from qx3learn_bot.config import WORDPAIR_TRANSCRIPTION_SEPARATOR
from qx3learn_bot.validators.base_validator import ValidatorBase
from qx3learn_bot.validators.wordpair.component_validator import ComponentValidator


class ItemValidator(ValidatorBase):
    """Валідатор для елементу словникової пари (слово з транскрипцією або переклад з транскрипцією).

    Notes:
        Приклад (self._item):
            "cat | кет"

        Приклад (self.item_components):
            ['cat', 'кет']
    """

    def __init__(self, item: str, errors: list[str] | None = None) -> None:
        super().__init__(errors)

        self._item: str = item
        self.item_components: list[str] = self._item.split(sep=WORDPAIR_TRANSCRIPTION_SEPARATOR, maxsplit=1)

    def _check_valid_word(self) -> bool:
        """Перевіряє, чи валідне слово елементу словникової пари"""
        word: str = self.item_components[0]
        is_valid_word: bool = ComponentValidator(component=word, errors=self.errors).is_valid()
        return is_valid_word

    def _check_valid_transcription(self) -> bool:
        """Перевіряє, чи валідна транскрипція елементу словникової пари.
        Якщо транскрипції немає (None), то вона вважається валідною.
        """
        transcription: str | None = self.item_components[1] if len(self.item_components) == 2 else None

        # Якщо транскрипції немає (вона не обовʼязкова)
        if transcription is None:
            return True

        is_valid_transcription: bool = ComponentValidator(component=transcription, errors=self.errors).is_valid()
        return is_valid_transcription

    def is_valid(self) -> bool:
        """Виконує всі перевірки для елементу словникової пари, та повертає прапор,
        чи успішно пройдені всі перевірки.
        """
        is_valid_word: bool = self._check_valid_word()
        is_valid_transcription: bool = self._check_valid_transcription()

        is_valid: bool = is_valid_word and is_valid_transcription
        return is_valid
