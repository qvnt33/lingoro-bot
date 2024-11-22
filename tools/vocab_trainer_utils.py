import random


def format_training_process_message(vocab_name: str,
                                    training_mode: str,
                                    wordpairs_left: int,
                                    total_wordpairs_count: int,
                                    words: str) -> str:
    """Форматує повідомлення з інформацією під час тренування"""
    summary_message: str = (
        f'📚 Словник: {vocab_name}\n'
        f'🔄 Тип тренування: {training_mode}\n\n'
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
    """Форматує підсумкове повідомлення зі інформацією про завершене тренування"""
    summary_message: str = (
        f'🎉 Тренування завершено!\n\n'
        f'📚 Словник: {vocab_name}\n'
        f'🔄 Тип тренування: {training_mode}\n\n'
        f'🎯 Пройдених тренувань поспіль: {training_streak_count}\n'
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
