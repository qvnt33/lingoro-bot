def create_vocab_message(vocab_name: str = None, vocab_note: str = None, content: str = '') -> str:
    """Створює форматоване повідомлення, яке включає назву словника, примітку та основний контент"""
    # Якщо vocab_name або vocab_note порожні, використовується значення за замовчуванням
    vocab_name = vocab_name or 'Відсутня'
    vocab_note = vocab_note or 'Відсутня'

    # Форматуємо повідомлення
    formatted_message: str = (
        f'Назва: {vocab_name}\n'
        f'Примітка: {vocab_note}\n\n'
        f'{content}'
    )
    return formatted_message
