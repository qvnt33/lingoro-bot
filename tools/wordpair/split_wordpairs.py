def split_wordpairs(input_text: str) -> list[tuple[list[str], list[str], str]]:
    """Розбиває введений користувачем рядок на окремі словникові пари"""
    wordpairs: list[str] = input_text.split('\n')  # Розбиття рядків на окремі словникові пари
    result = []

    for wordpair in wordpairs:
        parts = wordpair.split(':')  # Список частин словникової пари

        # Слова
        words = [word.strip() for word in parts[0].split(',')]

        # Переклади
        translations = [translation.strip() for translation in parts[1].split(',')] if len(parts) > 1 else []

        # Анотація
        annotation = parts[2].strip() if len(parts) > 2 else ""

        result.append((words, translations, annotation))

    return result
