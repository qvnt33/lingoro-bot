import asyncio  # noqa: I001
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
    logging.info('Запуск бота')

    create_tables()  # Створення всіх таблиць

    bot = Bot(token=TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher()

    register_handlers(dp)  # Підключення роутерів

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
