from . import create_vocab
from aiogram import Dispatcher


def register_handlers(dp: Dispatcher) -> None:
    """Реєструє усі хендлери"""
    from . import help, menu, vocab_base, vocab_trainer

    dp.include_router(menu.router)
    dp.include_router(help.router)
    dp.include_router(vocab_base.router)
    dp.include_router(create_vocab.router)
    dp.include_router(vocab_trainer.router)
