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
