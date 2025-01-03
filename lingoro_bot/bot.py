import asyncio
import json
import logging
import logging.config

from aiogram import Bot, Dispatcher

from qx3learn_bot.config import TOKEN
from qx3learn_bot.db.database import create_database_tables
from qx3learn_bot.handlers import register_handlers


async def main() -> None:
    create_database_tables()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # Конфігурація логування
    with open('logging.conf') as file:
        logging_config: dict = json.load(file)
    logging.config.dictConfig(logging_config)

    logger: logging.Logger = logging.getLogger()

    register_handlers(dp)

    logger.info('BOT START')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
