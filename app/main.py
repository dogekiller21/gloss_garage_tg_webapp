from fastapi import FastAPI, Depends
import uvicorn
from starlette.responses import RedirectResponse
from tortoise.contrib.fastapi import register_tortoise

import db
from app.auth import validate_tg_data, create_access_token, DataStringForm
from app.routes import (
    services,
    categories,
    users,
    cars,
    payment_methods,
    rendered_services,
)
from starlette.middleware.cors import CORSMiddleware

from db import User
from db.pydantic_models import UserOut_pydantic

app = FastAPI()
app.include_router(services.router)
app.include_router(categories.router)
app.include_router(users.router)
app.include_router(cars.router)
app.include_router(payment_methods.router)
app.include_router(rendered_services.router)


@app.post("/auth")
async def token(form_data: DataStringForm = Depends()):
    tg_id = validate_tg_data(form_data.data_string)
    user = await User.get_or_none(tg_id=tg_id)
    await user.fetch_related("is_sadmin")
    user_out = await UserOut_pydantic.from_tortoise_orm(user) if user is not None else None
    jwt_token, expiration_date = create_access_token(tg_id=tg_id)
    return {"token": jwt_token, "user": user_out}


@app.get("/")
async def home_page():
    return RedirectResponse(url="docs")


register_tortoise(app, config=db.TORTOISE_ORM, generate_schemas=True)

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
