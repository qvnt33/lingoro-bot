import random
from typing import Any

from qx3learn_bot.tools.wordpair_utils import format_word_items


def format_training_process_message(vocab_name: str,
                                    training_mode: str,
                                    wordpairs_left: int,
                                    total_wordpairs_count: int,
                                    words: str) -> str:
    """Форматує повідомлення з інформацією під час тренування.

    Args:
        vocab_name (str): Назва словника.
        training_mode (str): Тип тренування.
        wordpairs_left (int): Скільки пройдено (перекладено чи пропущено) словникових пар.
        total_wordpairs_count (int): Скільки всіх словникових пар у словнику.
        words (str): Відформатоване слово(а) (слова+транскрипції)
    """
    summary_message: str = (
        f'📗 Словник: {vocab_name}\n'
        f'🎯 Тип тренування: {training_mode}\n\n'
        f'📋 Прогрес: {wordpairs_left} / {total_wordpairs_count}\n\n'
        f'🔻 Перекладіть слово(а):\n'
        f'{words}')
    return summary_message


def format_training_summary_message(vocab_name: str,
                                    training_mode: str,
                                    training_streak_count: int,
                                    correct_answer_count: int,
                                    wrong_answer_count: int,
                                    annotation_shown_count: int,
                                    translation_shown_count: int,
                                    training_time_minutes: int,
                                    training_time_seconds: int) -> str:
    """Форматує підсумкове повідомлення зі інформацією про завершене тренування.

    Args:
        vocab_name (str): Назва словника.
        training_mode (str): Тип тренування.
        training_streak_count (int): Кількість пройдених тренувань поспіль.
        correct_answer_count (int): Кількість коректно перекладаних слів.
        wrong_answer_count (int): Кількість помилок.
        annotation_shown_count (int): Кількість показів анотацій за тренування.
        translation_shown_count (int): Кількість показів перекладів за тренування.
        training_time_minutes (int): Скільки хвилин йшло тренування (не враховуючи секунди).
        training_time_seconds (int): Скільки секунд йшло тренування (не враховуючи хвилини).

    Returns:
        str: Відформатована статистика тренування.
    """
    summary_message: str = (
        f'🎉 Тренування завершено!\n\n'
        f'📗 Словник: {vocab_name}\n'
        f'🎯 Тип тренування: {training_mode}\n\n'
        f'🔥 Пройдених тренувань поспіль: {training_streak_count}\n'
        f'✅ Коректно перекладено слів: {correct_answer_count}\n'
        f'❌ Кількість помилок: {wrong_answer_count}\n'
        f'💡 Показів анотацій: {annotation_shown_count}\n'
        f'💬 Показів перекладів: {translation_shown_count}\n\n'
        f'⏱ Тривалість тренування: {training_time_minutes} хвилин(а), {training_time_seconds} секунд(а)\n\n'
        '➡️ Оберіть, що робити далі:')
    return summary_message


def get_random_wordpair_idx(available_idxs: list, preview_idx: int) -> int:
    """Повертає випадковий індекс словникової пари із доступних.

    Notes:
        Якщо кількість доступних індексів більша за один, то обраний новий індекс не повинен збігатися з попереднім.

    Args:
        available_idxs (list): Список доступних індексів.
        preview_idx (int): Попередній індекс.

    Returns:
        int: Випадковий індекс.
    """
    if len(available_idxs) == 1:
        return available_idxs[0]

    # Якщо індексів більше одного, то обирається новий індекс
    wordpair_idx: int = random.choice(available_idxs)

    while wordpair_idx == preview_idx:
        wordpair_idx: int = random.choice(available_idxs)

    return wordpair_idx


def get_training_data(training_mode: str, word_items: list[dict], translation_items: list[dict]) -> dict[str, Any]:
    """Повертає дані для тренування, виходячи із типу тренування.

    Args:
        training_mode (str): Тип тренування.
        word_items (list[dict]): Список слів словникової пари з їх транскрипціями.
        translation_items (list[dict]): Список перекладів словникової пари з їх транскрипціями.

    Returns:
        dict[str, Any]: Python-словник із даними:
            training_mode_name (str): Назва тренування.
            formatted_words (str): Відформатовані слова словникової пари у вигляді рядка.
            formatted_translations (str): Відформатовані переклади словникової пари у вигляді рядка.
            correct_translations (list[str]): Список коректних перекладів у нижньому регістрі.
    """
    if training_mode == 'direct_translation':
        training_mode_name = 'Прямий переклад (W -> T)'
        formatted_words: str = format_word_items(word_items)
        formatted_translations: str = format_word_items(translation_items, is_translation_items=True)
        correct_translations: list[str] = [translation.get('translation').lower() for translation in translation_items]
    elif training_mode == 'reverse_translation':
        training_mode_name = 'Зворотній переклад (T -> W)'
        formatted_words: str = format_word_items(translation_items, is_translation_items=True)
        formatted_translations: str = format_word_items(word_items)
        correct_translations: list[str] = [translation.get('word').lower() for translation in word_items]

    training_data: dict[str, Any] = {'training_mode_name': training_mode_name,
                                     'formatted_words': formatted_words,
                                     'formatted_translations': formatted_translations,
                                     'correct_translations': correct_translations}
    return training_data


def get_wordpair_idx_for_training(available_idxs: list, preview_wordpair_idx: int, is_use_current_words: bool) -> int:
    """Повертає індекс словникової пари для тренування.

    Notes:
        Якщо is_use_current_words=True, то повертається попередній індекс,
        в іншому разі випадковий із списку невикористаних.

    Args:
        available_idxs (list): Список індексів, які ще не були використані.
        preview_wordpair_idx (int): Минулий індекс.
        is_use_current_words (bool): Прапор, використовувати поточне слово(а) чи обрати нове.
    """
    if is_use_current_words:
        return preview_wordpair_idx

    # Вибір випадкового індексу з тих, що ще не були використані
    return get_random_wordpair_idx(available_idxs, preview_wordpair_idx)
