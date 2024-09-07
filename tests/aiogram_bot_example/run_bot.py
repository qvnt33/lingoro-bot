import asyncio
import logging

from aiogram import Dispatcher, Bot

from core.handlers import register_handlers

from utils import set_bot_default_commands_private
from utils.db import DataBaseController


logger = logging.getLogger(__name__)


async def on_startup():
    # Объект логирования
    logging.basicConfig(level=logging.DEBUG,
                        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s", )

    # Уведомление о запуске бота
    logger.info("Бот запустился")

    # Инициализация бота
    bot: Bot = Bot(token="", parse_mode="HTML")
    dp: Dispatcher = Dispatcher()

    # Регистрация команд по умолчанию
    await set_bot_default_commands_private(bot)

    # Регистрация middleware
    ...

    # Регистрация handlers
    register_handlers(dp)
    
    db = DataBaseController(db_name="database.sqlite")

    # Удаление веб хуков, запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(
        bot,
        db=db,
        
    )


if __name__ == '__main__':
    try:
        asyncio.run(on_startup())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
