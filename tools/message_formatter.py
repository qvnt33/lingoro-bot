def add_vocab_data_to_message(vocab_name: str | None = None,
                              vocab_description: str | None = None,
                              message_text: str = '') -> str:
    """Додає до повідомлення назву та опис словника.

    Notes:
        - якщо не буде передана назва словника, то записується слово "Відсутня".
        - якщо не буде переданий опис словника, то записується слово "Відсутній".

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
        f'Назва: {vocab_name}\n'
        f'Опис: {vocab_description}\n\n'
        f'{message_text}'
    )
    return formatted_message
