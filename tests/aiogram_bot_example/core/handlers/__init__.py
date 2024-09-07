from aiogram import Dispatcher


def register_handlers(dp: Dispatcher):
    from . import user

    dp.include_routers(
        user.router,
    )