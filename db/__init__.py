from tortoise import Tortoise

from bot.constants import SUPREME_ADMINS_ID
from db.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME
from db.models import SupremeAdmin, User

TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
    },
    "apps": {
        "models": {
            "models": ["db.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}


async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)


async def init_admins():
    for admin_id in SUPREME_ADMINS_ID:
        user = await User.get_or_none(tg_id=admin_id)
        if user is None:
            print(f"{admin_id} is not a known user")
            return
        await SupremeAdmin.get_or_create(user=user)
