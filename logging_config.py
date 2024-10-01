import logging
from logging.handlers import RotatingFileHandler


def setup_logging() -> None:
    """Налаштовує логування з ротацією логів та спеціальним форматом для консолі"""
    # Ротаційний лог-файл: 5 MB на файл, зберігання до 3 архівів
    file_handler = RotatingFileHandler(
        filename='app.log',   # Назва лог-файлу
        maxBytes=1024 * 1024 * 5,  # Максимальний розмір лог-файлу - 5 МБ
        backupCount=3,  # Кількість збережених архівів логів
        mode='a',  # Додавання нових логів, а не перезаписування файлу
    )

    # Формат для запису у файл (детальний)
    file_format = logging.Formatter(
        fmt='%(asctime)s - [%(levelname)s] - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',  # Формат дати
    )
    file_handler.setFormatter(file_format)

    # Стандартний консольний хендлер з потрібним форматом
    console_handler = logging.StreamHandler()

    # Формат для виведення у консоль (логер, рівень, файл, рядок, повідомлення)
    console_format = logging.Formatter(
        fmt='%(asctime)s [%(levelname)-s] [%(filename)s:%(lineno)d] >> %(message)s <<',
        datefmt='%H:%M:%S',  # Формат дати
    )
    console_handler.setFormatter(console_format)

    # Отримання кореневого логера
    logger: logging.Logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Встановлюємо рівень логування

    # Додаємо обробники до логера
    logger.addHandler(file_handler)  # Додаємо обробник для файлу
    logger.addHandler(console_handler)  # Додаємо обробник для консолі

    # Зменшити рівень логування для aiogram
    logging.getLogger('aiogram').setLevel(logging.WARNING)
