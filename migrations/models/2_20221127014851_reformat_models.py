from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "bonusaccrual" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "bonus_count" INT NOT NULL,
    "created_time" TIMESTAMPTZ NOT NULL,
    "car_id" INT NOT NULL REFERENCES "car" ("id") ON DELETE CASCADE,
    "rendered_service_id" INT REFERENCES "renderedservice" ("id") ON DELETE SET NULL
);;
        CREATE TABLE IF NOT EXISTS "paymentmethod" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(20) NOT NULL
);;
        ALTER TABLE "renderedservice" ADD "payment_method_id" INT;
        ALTER TABLE "renderedservice" ADD CONSTRAINT "fk_rendered_paymentm_9c56de66" FOREIGN KEY ("payment_method_id") REFERENCES "paymentmethod" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "renderedservice" DROP CONSTRAINT "fk_rendered_paymentm_9c56de66";
        ALTER TABLE "renderedservice" DROP COLUMN "payment_method_id";
        DROP TABLE IF EXISTS "bonusaccrual";
        DROP TABLE IF EXISTS "paymentmethod";"""
