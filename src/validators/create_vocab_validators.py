def validate_vocab_name(vocab_name: str) -> bool:
    """Перевіряє назву словника"""

    if len(vocab_name) < 3:
        return False  # Назва повинна бути щонайменше 3 символи
    if any(char.isdigit() for char in vocab_name):
        return False  # Назва не повинна містити цифр
    return True
