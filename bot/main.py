import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types.web_app_info import WebAppInfo

import db
from bot.config import FRONT_END_LINK
from bot.middlewares import UserMiddleware
from config import TG_TOKEN

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)

webapp_info = WebAppInfo(url=FRONT_END_LINK)


if __name__ == "__main__":
    from handlers import dp

    dp.setup_middleware(UserMiddleware())
    loop = asyncio.new_event_loop()
    loop.run_until_complete(db.init_db())
    loop.run_until_complete(db.init_admins())
    loop.create_task(
        dp.start_polling(
            reset_webhook=None, timeout=20, relax=0.1, fast=True, allowed_updates=None
        )
    )
    loop.run_forever()
