from fastapi import FastAPI, Depends, HTTPException
import uvicorn
from starlette.status import (
    HTTP_409_CONFLICT,
)
from tortoise.contrib.fastapi import register_tortoise

from app.auth import (
    validate_tg_data,
    create_access_token,
    DataStringForm, JWTBearer,
)
from app.routes import services, categories
from db import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME
from db.models import User, ServiceCategoryPrice
from starlette.middleware.cors import CORSMiddleware

from db.pydantic_models import (
    User_pydantic,
    ServiceCategoryPrice_pydantic,
    BoundServiceCategory,
)

app = FastAPI()
app.include_router(services.router)
app.include_router(categories.router)


@app.post("/auth")
async def token(form_data: DataStringForm = Depends()):
    tg_id = validate_tg_data(form_data.data_string)

    jwt_token, expiration_date = create_access_token(tg_id=tg_id)
    return {"token": jwt_token, "expiration_date": expiration_date}


@app.get("/")
async def home_page(user: User = Depends(JWTBearer())):
    return {"message": "yo", "id": user.id}


@app.get("/users")
async def get_users():
    users = await User_pydantic.from_queryset(User.all())
    return {"users": users}


register_tortoise(
    app,
    db_url=f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}",
    modules={"models": ["db.models"]},
    generate_schemas=True,
)

origins = [
    "http://localhost:8080",
    "https://bbf5-188-243-182-68.eu.ngrok.io/",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        app="main:app", host="localhost", port=8080, loop="asyncio", reload=True
    )
