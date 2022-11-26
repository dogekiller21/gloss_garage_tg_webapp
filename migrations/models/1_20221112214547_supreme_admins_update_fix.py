from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "supremeadmin" ADD "user_id" INT;
        ALTER TABLE "supremeadmin" DROP COLUMN "tg_id";
        ALTER TABLE "supremeadmin" ADD CONSTRAINT "fk_supremea_user_9237b85a" FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "supremeadmin" DROP CONSTRAINT "fk_supremea_user_9237b85a";
        ALTER TABLE "supremeadmin" ADD "tg_id" BIGINT NOT NULL;
        ALTER TABLE "supremeadmin" DROP COLUMN "user_id";"""
