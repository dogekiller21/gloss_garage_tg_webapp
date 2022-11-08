from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "carcategory" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(50) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "service" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL UNIQUE,
    "self_cost" INT NOT NULL
);
CREATE TABLE IF NOT EXISTS "servicecategoryprice" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "default_price" INT NOT NULL,
    "category_id" INT NOT NULL REFERENCES "carcategory" ("id") ON DELETE CASCADE,
    "service_id" INT NOT NULL REFERENCES "service" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "supremeadmin" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tg_id" BIGINT NOT NULL
);
CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tg_id" BIGINT NOT NULL UNIQUE,
    "name" VARCHAR(255) NOT NULL,
    "username" VARCHAR(255) NOT NULL,
    "created_time" TIMESTAMPTZ NOT NULL,
    "is_admin" BOOL NOT NULL  DEFAULT False
);
CREATE TABLE IF NOT EXISTS "car" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "brand" VARCHAR(30),
    "model" VARCHAR(50),
    "numberplate" VARCHAR(50) NOT NULL,
    "category_id" INT REFERENCES "carcategory" ("id") ON DELETE SET NULL,
    "owner_id" INT REFERENCES "user" ("id") ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS "renderedservice" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "price" INT NOT NULL,
    "comment" TEXT,
    "created_time" TIMESTAMPTZ NOT NULL,
    "car_id" INT NOT NULL REFERENCES "car" ("id") ON DELETE CASCADE,
    "service_id" INT NOT NULL REFERENCES "service" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
