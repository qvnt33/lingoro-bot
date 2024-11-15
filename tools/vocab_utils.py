from db.crud import VocabCRUD
from db.models import Vocabulary


def check_vocab_name_duplicate(vocab_name: str, vocab_name_old: str) -> bool:
    """Перевіряє, чи збігається нова назва словника з поточною"""
    return vocab_name_old is not None and vocab_name.lower() == vocab_name_old.lower()


def format_valid_wordpairs(wordpairs: list[str] | None) -> str:
    """Повертає відформатовані валідні словникові пари"""
    if wordpairs is None:
        formatted_valid_wordpairs = '-'
    else:
        formatted_valid_wordpairs: str = '\n'.join((f'{num}. {wordpair}'
                                                    for num, wordpair in enumerate(iterable=wordpairs,
                                                                                   start=1)))
    return formatted_valid_wordpairs
