from tortoise import Tortoise
from .config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME


async def init_db():
    await Tortoise.init(
        db_url=f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}",
        modules={"models": ["db.models"]},
    )
    await Tortoise.generate_schemas(safe=True)
