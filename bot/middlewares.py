import logging

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from constants import SUPREME_ADMINS_ID
from db.models import User, SupremeAdmin


class UserMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        user, is_created = await User.get_or_create(
            tg_id=message.from_user.id,
            defaults={
                "name": message.from_user.full_name,
                "username": message.from_user.username,
                "is_admin": message.from_user.id in SUPREME_ADMINS_ID,
            },
        )
        if is_created:
            logging.info(f"User added: {user}")
        data["current_user"] = user
        data["is_supremacy_admin"] = await SupremeAdmin.exists(
            tg_id=message.from_user.id
        )
