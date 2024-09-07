from aiogram import Bot
from aiogram.types import BotCommandScopeAllPrivateChats, BotCommand


async def set_bot_default_commands_private(bot: Bot):
    """
    Устанавливает список команд по умолчанию для бота во всех приватных чатах.

    :param bot: Экземпляр класса Bot, для которого устанавливаются команды.
    """

    # Доступные команды
    commands = [
        BotCommand(
            command="/jobs_list",
            description="Тендеры в работе"
        ),
        
        BotCommand(
            command="/sub_list",
            description="Заявки поданы"
        ),

        BotCommand(
            command="/remove_list",
            description="Удаленные тендеры"
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeAllPrivateChats())

