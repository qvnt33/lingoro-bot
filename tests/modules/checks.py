import re


class Check:
    """
    Класс для различных проверок.
    """

    @staticmethod
    def check_input_completed(user_input: tuple) -> bool:
        """
        Проверка: закончил ли пользователь вводить пак слов (без учета пробелов).
        """

        pure_user_input = user_input.strip()  # Ввод без пробелов
        is_input_completed = len(pure_user_input) == 0

        return is_input_completed

    @staticmethod
    def check_wordpair_in_wordpack(wordpair: tuple,
                                   wordpack: list) -> bool:
        """
        Проверка: состоит ли введенная пользователем пара слов в паке.
        """

        is_wordpair_in_pack = wordpair in wordpack
        return is_wordpair_in_pack

    @staticmethod
    def check_wordpair_empty(wordpair: str,
                             separator_chars: str = '-:') -> bool:
        """
        Проверка: пустое ли слово или перевод, принятой пары слов.
        """

        pattern = re.compile(rf'(.+?)\s*[{separator_chars}]+\s*(.+)')
        match = pattern.match(wordpair)

        word = match.group(1)  # Слово
        translation = match.group(2)  # Перевод

        is_word_empty = len(word.strip()) == 0  # Пустое ли слово
        is_translation_empty = len(translation.strip()) == 0  # Пустой ли перевод

        is_wordpair_empty = is_word_empty or is_translation_empty

        return is_wordpair_empty

    @staticmethod
    def check_valid_wordpair_separator(wordpair: str,
                                       separator_chars: str = '-:') -> bool:
        """
        Проверка: правильный ли разделитель пары слов.
        """

        pattern = re.compile(rf'(.+?)\s*[{separator_chars}]+\s*(.+)')
        match = pattern.match(wordpair)

        is_valid_separator = match is not None
        return is_valid_separator

    @staticmethod
    def check_empty_pack(pack: list) -> bool:
        """
        Проверка: пустой ли пак.
        """

        is_empty_pack = len(pack) == 0
        return is_empty_pack
