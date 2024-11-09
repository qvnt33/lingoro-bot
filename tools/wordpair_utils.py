def format_valid_wordpairs(wordpairs: list[str] | None) -> str:
    """Повертає відформатовані валідні словникові пари"""
    if wordpairs is None:
        formatted_valid_wordpairs = '-'
    else:
        formatted_valid_wordpairs: str = '\n'.join([f'{num}. {wordpair}'
                                                    for num, wordpair in enumerate(iterable=wordpairs,
                                                                                   start=1)])
    return formatted_valid_wordpairs


def format_invalid_wordpairs(wordpairs: list[dict] | None) -> str:
    """Повертає відформатовані не валідні словникові пари"""
    if wordpairs is None:
        formatted_invalid_wordpairs = '-'
    else:
        formatted_invalid_wordpairs: str = '\n\n'.join([f'{num}. {wordpair['wordpair']}\n{wordpair['errors']}'
                                                        for num, wordpair in enumerate(iterable=wordpairs,
                                                                                       start=1)])
    return formatted_invalid_wordpairs


def parse_wordpair_components(wordpair: str) -> dict:
    """Розділяє словникову пару на окремі компоненти: слова з транскрипціями, переклади з транскрипціями та анотацію.

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
        dict: Словник із ключами:
            - 'words': list[dict] — список словників із словами та їх транскрипції (якщо немає, то None),
            - 'translations': list[dict] — список словників із перекладами та їх транскрипції (якщо немає, то None),
            - 'annotation': str | None — анотація (якщо немає, то None).

    Example:
        >>> parse_wordpair_components('hello | хелоу, hi | хай : привіт, вітаю : загальна форма вітання')
        {
            'words': [
                {'word': 'hello', 'transcription': 'хелоу'},
                {'word': 'hi', 'transcription': 'хай'}
                ],
            'translations': [
                {'translation': 'привіт', 'transcription': None},
                {'word': 'вітаю', 'transcription': None}
                ],
            'annotation': 'загальна форма вітання'
        }
    """
    wordpair_parts: list[str] = wordpair.split(WORDPAIR_SEPARATOR)

    part_of_words: str = wordpair_parts[0]
    part_of_translation: str = wordpair_parts[1] if len(wordpair_parts) >= 2 else None
    part_of_annotation: str = wordpair_parts[2] if len(wordpair_parts) >= 3 else None

    words: list[str] = part_of_words.split(sep=WORDPAIR_TRANSCRIPTION_SEPARATOR, maxsplit=1)
    translations: list[str] = part_of_translation.split(sep=WORDPAIR_TRANSCRIPTION_SEPARATOR, maxsplit=1)

    return {
        "words": words_with_transcriptions,
        "translations": translations_with_transcriptions,
        "annotation": annotation
    }

# ?
def check_has_valid_wordpairs(data_fsm: dict) -> bool:
    """Перевіряє, чи є валідні словникові пари в FSM-кеші"""
    all_valid_wordpairs: list[str] | None = data_fsm.get('all_valid_wordpairs')
    return bool(all_valid_wordpairs)
