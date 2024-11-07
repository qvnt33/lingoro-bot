
def format_invalid_wordpairs(wordpairs: list[dict]) -> str:
    """Повертає відформатовані не валідні словникові пари"""
    formatted_invalid_wordpairs: str = '\n\n'.join([f'{num}. {wordpair['wordpair']}\n{wordpair['errors']}'
                                                    for num, wordpair in enumerate(iterable=wordpairs,
                                                                                   start=1)])
    return formatted_invalid_wordpairs


def format_valid_wordpairs(wordpairs: list[str]) -> str:
    """Повертає відформатовані валідні словникові пари"""
    formatted_valid_wordpairs: str = '\n'.join([f'{num}. {wordpair}'
                                                for num, wordpair in enumerate(iterable=wordpairs,
                                                                               start=1)])
    return formatted_valid_wordpairs


def format_wordpairs(wordpairs: list) -> str:
    """Повертає відформатовані валідні словникові пари"""
    formatted_valid_wordpairs: str = '\n'.join([f'{num}. {wordpair}'
                                                for num, wordpair in enumerate(iterable=wordpairs,
                                                                               start=1)])
    return formatted_valid_wordpairs
