from typing import Any

from fastapi import HTTPException, Depends
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from tortoise import Model

from app.auth import jwt_dependency
from db import SupremeAdmin
from db.models import Service, CarCategory, User, Car, PaymentMethod


async def user_depend(payload=Depends(jwt_dependency)) -> User:
    tg_id = payload["tg_id"]
    user = await User.get_or_none(tg_id=tg_id)
    if user is None:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="User not found")
    await user.fetch_related("is_sadmin", "cars")
    return user


async def admin_depend(user=Depends(user_depend)) -> User:
    if not user.is_admin:
        raise HTTPException(HTTP_403_FORBIDDEN, detail="Not an admin")
    return user


async def sadmin_depend(user=Depends(admin_depend)) -> User:
    if not user.is_sadmin:
        raise HTTPException(HTTP_403_FORBIDDEN, detail="Not a supreme admin")
    return user


async def get_obj_by_pk(model, pk: int | Any) -> Model | Any:
    item = await model.get_or_none(pk=pk)
    if item is None:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Does not exist")
    return item


async def get_service_depend(service_id: int) -> Service:
    return await get_obj_by_pk(model=Service, pk=service_id)


async def get_category_depend(category_id: int) -> CarCategory:
    return await get_obj_by_pk(model=CarCategory, pk=category_id)


async def get_car_depend(car_id: int) -> Car:
    return await get_obj_by_pk(model=Car, pk=car_id)


async def get_payment_method_depend(payment_method_id: int) -> Car:
    return await get_obj_by_pk(model=PaymentMethod, pk=payment_method_id)
