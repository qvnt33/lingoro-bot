from lingoro_bot.config import WORDPAIR_ITEM_SEPARATOR, WORDPAIR_SEPARATOR, WORDPAIR_TRANSCRIPTION_SEPARATOR
from lingoro_bot.custom_types.wordpair_types import (
    BaseWordpairTranslationType,
    BaseWordpairWordType,
    WordpairComponentsType,
)


def format_valid_wordpairs(wordpairs: list[str] | None) -> str:
    """Повертає відформатовані валідні словникові пари"""
    if wordpairs is None:
        return '-'

    formatted_valid_wordpairs: str = '\n'.join((f'{num}. {wordpair}' for num, wordpair in
                                                enumerate(wordpairs, start=1)))
    return formatted_valid_wordpairs


def format_invalid_wordpairs(wordpairs: list[dict[str, str]] | None) -> str:
    """Повертає відформатовані не валідні словникові пари"""
    if wordpairs is None:
        return '-'

    formatted_invalid_wordpairs: str = '\n\n'.join((f'{num}. {wordpair["wordpair"]}\n{wordpair["errors"]}'
                                                    for num, wordpair in enumerate(wordpairs, start=1)))
    return formatted_invalid_wordpairs


def format_wordpair_info(idx: int,
                         words: list[str],
                         translations: list[str],
                         annotation: str,
                         number_errors: int) -> str:
    """Повертає відформатовані не валідні словникові пари"""
    formatted_wordpair_info: str = (f'{idx}. {words} ▪️ {translations} ▪️ {annotation}\n'
                                    f'🔺 Помилки: {number_errors}\n')

    return formatted_wordpair_info


def parse_wordpair_components(wordpair: str) -> WordpairComponentsType:
    """Повертає розділену словникову пару на окремі компоненти:
    слова з транскрипціями, переклади з транскрипціями та анотацію.

    Notes:
        Приймається завжди тільки перевірена словникова пара.

    Args:
        wordpair (str): Словникова пара у форматі:
            "w1 | tr1 , w2 | tr2 : t1, t2 : a"
            - w — слово (обовʼязково)
            - t — переклад (обовʼязково)
            - tr — транскрипція (опціонально)
            - a — анотація (опціонально)
        *Слів та перекладів може бути декілька або лише по одному.

    Returns:
        WordpairComponentsType: Словник із ключами:
            - "words": list[BaseWordpairWordType] — список словників із словами та
            їх транскрипції (якщо немає, то None),
            - "translations": list[BaseWordpairTranslationType] — список словників із перекладами та
            їх транскрипції (якщо немає, то None),
            - "annotation": str | None — анотація (якщо немає, то None).

    Example:
        >>> parse_wordpair_components('hello | хелоу, hi | хай : привіт, вітаю : загальна форма вітання')
        {
            'words': [
                {'word': 'hello', 'transcription': 'хелоу'},
                {'word': 'hi', 'transcription': 'хай'}
                ],
            'translations': [
                {'translation': 'привіт', 'transcription': None},
                {'translation': 'вітаю', 'transcription': None}
                ],
            'annotation': 'загальна форма вітання'
        }
    """
    wordpair_components: WordpairComponentsType = {'words': [], 'translations': [], 'annotation': None}
    wordpair_words: list[BaseWordpairWordType] = []
    wordpair_translations: list[BaseWordpairTranslationType] = []

    # Розділення словникової пари по частинам
    wordpair_parts: list[str] = wordpair.split(WORDPAIR_SEPARATOR)
    part_of_words: str = wordpair_parts[0]
    part_of_translation: str = wordpair_parts[1]

    # Розділення частин словникової пари на елементи
    item_of_words: list[str] = part_of_words.split(WORDPAIR_ITEM_SEPARATOR)
    item_of_translations: list[str] = part_of_translation.split(WORDPAIR_ITEM_SEPARATOR)

    # Розділення елементів словникової пари на компоненти
    wordpair_annotation: str | None = wordpair_parts[2].strip() if len(wordpair_parts) == 3 else None

    for word_item in item_of_words:
        word, word_transcription = _parse_item_transcription(word_item)
        wordpair_words.append({'word': word,
                               'transcription': word_transcription})

    for translation_item in item_of_translations:
        translation, translation_transcription = _parse_item_transcription(translation_item)
        wordpair_translations.append({'translation': translation,
                                      'transcription': translation_transcription})

    wordpair_components['words'] = wordpair_words
    wordpair_components['translations'] = wordpair_translations
    wordpair_components['annotation'] = wordpair_annotation

    return wordpair_components


def _parse_item_transcription(item: str) -> tuple[str, str | None]:
    """Розділяє елемент словникової пари на компоненти: слово та транскрипцію.

    Args:
        item (str): Частина словникової пари (слово з транскрипцією чи переклад з транскрипцією).

    Returns:
        tuple[str, str | None]: Кортеж із компонента та його транскрипції (якщо немає, то None).
    """
    parsed_item: str = item.split(WORDPAIR_TRANSCRIPTION_SEPARATOR)  # Розділений елемент

    component: str = parsed_item[0].strip()
    transcription: str | None = parsed_item[1].strip() if len(parsed_item) == 2 else None

    return component, transcription


def format_word_items(word_items: list[dict], is_translation_items: bool = False) -> str:
    """Розділяє всі переданні слова на слова та транскрипції (якщо є), після форматує їх у рядок.

    Args:
        word_items (list[dict]):
            Приклад (word_items):
                [
                    {'word': 'кіт', 'transcription': None},
                    {'word': 'собака', 'transcription': None},
                ]
                або
                [
                    {'translation': 'cat', 'transcription': 'кет'},
                    {'translation': 'dog', 'transcription': None},
                ]
        is_translation_items (bool): Прапор, чи передані слова є перекладами (translation).

    Returns:
        str: Список відформатованих частин слів.

    Examples:
        >>> format_word_items(word_items=[{'translation': 'cat', 'transcription': 'кет'},
                                          {'translation': 'dog', 'transcription': None],
                              is_translation_items=True)
        "cat [кет], dog"
    """
    formatted_words: list[str] = []

    for word_item in word_items:
        word: str = word_item.get('translation') if is_translation_items else word_item.get('word')

        transcription: str | None = word_item.get('transcription')

        formatted_word: str = (f'{word} [{transcription}]'
                               if transcription is not None else word)
        formatted_words.append(formatted_word)

    joined_words: str = ', '.join(formatted_words)
    return joined_words


def get_formatted_wordpairs_list(wordpair_items: list[dict]) -> list[str]:
    """Повертає список відформатованих словникових пар.

    Args:
        wordpair_items (list[dict]): Список словникових пар з інформацією про них.

    Returns:
        list[str]: Список з відформатованими словниковими парами.
    """
    formatted_wordpairs: list[str] = []

    for idx, wordpair_item in enumerate(wordpair_items, start=1):
        word_items: list[dict] = wordpair_item.get('words')
        translation_items: list[dict] = wordpair_item.get('translations')
        annotation: str = wordpair_item.get('annotation') or 'Немає анотації'
        wordpair_number_errors: int = wordpair_item.get('number_errors')

        formatted_word_items: list[str] = format_word_items(word_items)
        formatted_translation_items: list[str] = format_word_items(translation_items, is_translation_items=True)

        formatted_wordpair: str = format_wordpair_info(idx=idx,
                                                       words=formatted_word_items,
                                                       translations=formatted_translation_items,
                                                       annotation=annotation,
                                                       number_errors=wordpair_number_errors)
        formatted_wordpairs.append(formatted_wordpair)
    return formatted_wordpairs
