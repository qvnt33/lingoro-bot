def check_vocab_name_duplicate(vocab_name: str, vocab_name_old: str) -> bool:
    """Перевіряє, чи збігається нова назва словника з поточною

    Args:
        vocab_name (str): Нова назва словника.
        vocab_name_old (str): Поточна назва словника.

    Returns:
        bool: Прапор, чи є поточне слово та чи збігається воно з новим (незважаючи на регістр).
    """
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


def add_vocab_data_to_message(vocab_name: str | None = None,
                              vocab_description: str | None = None,
                              message_text: str = '') -> str:
    """Додає до повідомлення назву та опис словника.

    Notes:
        - Якщо не буде передана назва словника, то записується слово "Відсутня".
        - Якщо не буде переданий опис словника, то записується слово "Відсутній".

    Args:
        vocab_name (str | None): Назва словника (за замовчуванням: None).
        vocab_description (str | None): Опис словника (за замовчуванням: None).
        message_text (str): Повідомлення, до якого потрібно додати інформацію про словник
        (за замовчуванням пустий рядок).

    Returns:
        str: Відредаговане повідомлення з доданою назвою та описом словника.
    """
    vocab_name = vocab_name or 'Відсутня'
    vocab_description = vocab_description or 'Відсутній'

    formatted_message: str = (
        f'📗 Назва: {vocab_name}\n'
        f'📄 Опис: {vocab_description}\n\n'
        f'{message_text}')
    return formatted_message
