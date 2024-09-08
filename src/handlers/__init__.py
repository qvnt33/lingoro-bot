from aiogram import Dispatcher


def register_handlers(dp: Dispatcher) -> None:
    """Реєструємо усі хендлери"""
    from . import (menu,
                   help,
                   dict_base,
                   word_trainer)

    dp.include_router(menu.router)
    dp.include_router(help.router)
    dp.include_router(dict_base.router)
    dp.include_router(word_trainer.router)
