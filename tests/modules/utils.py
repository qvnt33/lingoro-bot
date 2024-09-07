import os

from texttable import Texttable

from config import Config


class Utility:
    """
    Класс полезных утилит.
    """

    @staticmethod
    def get_combining_wordpair(separated_wordpair: tuple,
                               separator_word: str = ', ',
                               separator_wordpair: str = ' - ') -> str:
        """
        Объединение пары слов по заданному разделителю, для корректного визуального отображения.
        """

        word_list = separated_wordpair[0]  # Список слов
        translation_list = separated_wordpair[1]  # Список переводов

        combined_words = separator_word.join(word_list)  # Объединенные слова
        combined_translation = separator_word.join(translation_list)  # Объединенные переводы

        combined_wordpair = separator_wordpair.join([combined_words,
                                                     combined_translation])  # Объединенная пара слов
        return combined_wordpair

    @staticmethod
    def clear_console() -> None:
        """
        Очистка консоли, исходя из операционной системы.
        """

        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def get_text_color(type_text: str) -> str:
        """
        Возвращает цвет, исходя из типа текста.
        """

        if type_text == 'Error':
            text_color = Config.COLORS['red']
        elif type_text == 'Valid':
            text_color = Config.COLORS['cyan']
        elif type_text == 'Simple':
            # Если цвет не требуется
            text_color = ''
        else:
            raise ValueError(f'Неизвестный тип текста: {type_text}')

        return text_color

    @staticmethod
    def formatted_print(text: str,
                        type_text: str = 'Simple',
                        clear_console: bool = True) -> None:
        """
        Вывод отформатированного текста, добавляя обводку и цвет, исходя от типа текста.
        По надобности происходит очистка консоли.
        """

        if clear_console:
            Utility.clear_console()

        table = Texttable()

        text_color = Utility.get_text_color(type_text=type_text)  # Выбранный цвет текста
        table.add_row([text])  # Создания обводки

        # Элементы для форматирования текста
        formatting_elements = [text_color,
                               table.draw(),
                               Config.COLORS['color_reset']]
        formatted_text = ''.join(formatting_elements)  # Отформатированный текст
        print(formatted_text)
