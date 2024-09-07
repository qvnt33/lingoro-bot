import asyncio

from aiogram import Bot, Dispatcher

from config import TOKEN
from src.handlers import register_handlers


async def main():
    bot = Bot(token=TOKEN)

    dp = Dispatcher()
    register_handlers(dp)  # Підключення роутерів

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
