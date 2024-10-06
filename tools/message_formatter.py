def format_message(vocab_name: str = None, vocab_note: str = None, content: str = '') -> str:
    """Форматує повідомлення бота з заголовком і основним контентом"""
    # Якщо vocab_name або vocab_note порожні, використовуємо значення за замовчуванням
    vocab_name = vocab_name or 'Відсутня'
    vocab_note = vocab_note or 'Відсутня'

    # Форматуємо повідомлення
    formatted_message: str = (
        f'Назва: {vocab_name}\n'
        f'Примітка: {vocab_note}\n\n'
        f'{content}'
    )
    return formatted_message
