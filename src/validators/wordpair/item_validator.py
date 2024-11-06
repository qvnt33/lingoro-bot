
from config import WORDPAIR_TRANSCRIPTION_SEPARATOR
from src.validators.base_validator import ValidatorBase
from src.validators.wordpair.component_validator import ComponentValidator


class ItemValidator(ValidatorBase):
    """Валідатор для елементів словникової пари (слово з транскрипцією або переклад з транскрипцією)"""

    def __init__(self, item: str, errors: list = None) -> None:
        super().__init__(errors)

        self._item: str = item
        self.item_components: list[str] = self._item.split(sep=WORDPAIR_TRANSCRIPTION_SEPARATOR,
                                                           maxsplit=1)

    def _check_valid_word(self) -> bool:
        item_of_word: str = self.item_components[0]
        is_valid_word: bool = ComponentValidator(component=item_of_word,
                                                 errors=self.errors).is_valid()
        return is_valid_word

    def _check_valid_transcription(self) -> bool:
        item_of_transcription: str | None = self.item_components[1] if len(self.item_components) == 2 else None

        # Якщо транскрипції немає
        if item_of_transcription is None:
            return True

        is_valid_transcription: bool = ComponentValidator(component=item_of_transcription,
                                                          errors=self.errors).is_valid()
        return is_valid_transcription

    def is_valid(self) -> bool:
        is_valid_word: bool = self._check_valid_word()
        is_valid_transcription: bool = self._check_valid_transcription()

        is_valid: bool = is_valid_word and is_valid_transcription
        return is_valid
