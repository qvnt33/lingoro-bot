import asyncio
import logging  # Імпорт логування
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from config import TOKEN
from db.models import create_tables
from logging_config import setup_logging  # Імпорт налаштувань логування
from src.handlers import register_handlers


async def main() -> None:
    setup_logging()  # Налаштування логування на самому початку програми
    logging.info("Старт програми")

    create_tables()  # Створення всіх таблиць
    logging.info("Таблиці в базі даних створені")

    bot = Bot(token=TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher()

    register_handlers(dp)  # Підключення роутерів
    logging.info("Хендлери підключені")

    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Вебхук видалено, починається полінг")

    await dp.start_polling(bot)
    logging.info("Полінг запущено")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    finally:
        # Примусово скидаємо всі логи у файл після завершення
        logging.shutdown()
