import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import TOKEN
from db.database import create_database_tables
from logging_config import setup_logging
from src.handlers import register_handlers


async def main() -> None:
    setup_logging()
    create_database_tables()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    register_handlers(dp)

    logging.info('BOT START')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
