def format_message(vocab_name: str = 'Відсутня', vocab_note: str = 'Відсутня', content: str = '') -> str:
    """Форматує повідомлення бота з заголовком і основним контентом"""
    formatted_message: str = (
        f'Назва: {vocab_name}\n'
        f'Примітка: {vocab_note}\n\n'
        f'{content}'
)
    return formatted_message
