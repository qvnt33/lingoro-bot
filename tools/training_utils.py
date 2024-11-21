def format_training_message(vocab_name: str,
                            training_mode: str,
                            training_count: int,
                            number_errors: int,
                            word: str) -> str:
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
    formatted_message: str = (
        f'Словник: {vocab_name}\n'
        f'Тип: {training_mode}\n'
        f'Лічильник тренувань: {training_count}\n'
        f'Помилки: {number_errors}\n\n'
        f'Перекладіть слово(а): {word}')
    return formatted_message
