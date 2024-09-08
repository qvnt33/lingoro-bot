from aiogram import Dispatcher


def register_handlers(dp: Dispatcher) -> None:
    """Реєструємо усі хендлери"""
    from . import (menu,
                   help,
                   vocab_base,
                   vocab_trainer)

    dp.include_router(menu.router)
    dp.include_router(help.router)
    dp.include_router(vocab_base.router)
    dp.include_router(vocab_trainer.router)
