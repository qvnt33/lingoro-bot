def check_vocab_name_duplicate(vocab_name: str, vocab_name_old: str) -> bool:
    """Перевіряє, чи збігається нова назва словника з поточною"""
    return vocab_name_old is not None and vocab_name.lower() == vocab_name_old.lower()
