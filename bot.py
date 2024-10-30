import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import TOKEN
from db.models import create_tables
from logging_config import setup_logging
from src.handlers import register_handlers


async def main() -> None:
    setup_logging()
    create_tables()

    bot = Bot(token=TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher()

    register_handlers(dp)

    logging.info('Запуск бота')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
