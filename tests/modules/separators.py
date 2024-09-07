import re


class Separator:
    """
    Класс для разделения пары слов.
    """

    @staticmethod
    def get_separated_wordpair(wordpair: str,
                               separator_chars: str = '-:') -> tuple:
        """
        Разделение пары на слово и перевод, с помощью переданного разделителя.
        """

        pattern = re.compile(rf'(.+?)\s*[{separator_chars}]+\s*(.+)')
        match = pattern.match(wordpair)

        word = match.group(1)  # Слово
        translation = match.group(2)  # Перевод

        # Разделение слов или переводов
        separated_wordpair = Separator._get_separated_words(word,
                                                            translation)
        return separated_wordpair

    @staticmethod
    def _get_separated_words(word: str,
                             translation: str,
                             separator_chars: str = ',') -> tuple:
        """
        Разделение слов или переводов по переданному разделителю.
        Если их несколько.
        """

        # Разделение слов по разделителю
        separated_words = re.split(rf'\s*{separator_chars}\s*',
                                   word)

        # Разделение переводов по разделителю
        separated_translations = re.split(rf'\s*{separator_chars}\s*',
                                          translation)

        # Кортеж слова и перевода
        tuple_pair = (separated_words,
                      separated_translations)
        return tuple_pair
