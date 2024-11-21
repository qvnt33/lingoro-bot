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
        f'Назва: {vocab_name}\n'
        f'Опис: {vocab_description}\n\n'
        f'{message_text}')
    return formatted_message





def del_add_section_title_to_message(message_text: str, section: str) -> str:
    """Додає назву поточного розділу до повідомлення.

    Notes:
        - Якщо не буде передана назва розділу, то записується слово "Відсутня".

    Args:
        section_title (str | None): Назва розділу (за замовчуванням: None).
        message_text (str): Повідомлення, до якого потрібно додати назву розділу
        (за замовчуванням пустий рядок).

    Returns:
        str: Відредаговане повідомлення з доданою назвою розділу.
    """
    if section == 'training':
        section_title = 'Словниковий тренажер'
    elif section == 'vocab_base':
        section_title = 'База словників'

    formatted_message: str = (
        f'📂 {section_title}\n\n'
        f'{message_text}')
    return formatted_message
