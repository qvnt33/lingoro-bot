def add_vocab_data_to_message(vocab_name: str | None = None,
                              vocab_description: str | None = None,
                              message_text: str = '') -> str:
    """Додає до повідомлення назву та опис словника"""
    vocab_name = vocab_name or 'Відсутня'
    vocab_description = vocab_description or 'Відсутній'

    formatted_message: str = (
        f'Назва: {vocab_name}\n'
        f'Опис: {vocab_description}\n\n'
        f'{message_text}'
    )
    return formatted_message
