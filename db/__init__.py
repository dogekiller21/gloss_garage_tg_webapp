from tortoise import Tortoise

from bot.constants import SUPREME_ADMINS_ID
from db.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME
from db.models import SupremeAdmin


async def init_db():
    await Tortoise.init(
        db_url=f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}",
        modules={"models": ["db.models"]},
    )
    await Tortoise.generate_schemas(safe=True)


async def init_admins():
    for admin_id in SUPREME_ADMINS_ID:
        await SupremeAdmin.get_or_create(tg_id=admin_id)
