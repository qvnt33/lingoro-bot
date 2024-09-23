import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from config import TOKEN
from db.models import create_tables
from src.handlers import register_handlers


async def main() -> None:
    bot = Bot(token=TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

    dp = Dispatcher()
    register_handlers(dp)  # Підключення роутерів

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    create_tables()  # Створення всіх таблиць
    asyncio.run(main())
