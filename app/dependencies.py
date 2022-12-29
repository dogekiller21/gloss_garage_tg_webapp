from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, Depends, Query
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from tortoise import Model

from app.auth import jwt_dependency
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
        raise HTTPException(HTTP_404_NOT_FOUND, detail=f"{model.__name__} does not exist")
    return item


async def model_getter(pk: Any, model) -> Model | Any:
    if pk is None:
        return
    return await get_obj_by_pk(model=model, pk=pk)


async def get_service_depend(service_id: int = Query(None)) -> Service | None:
    return await model_getter(pk=service_id, model=Service)


async def get_category_depend(category_id: int = Query(None)) -> CarCategory | None:
    return await model_getter(pk=category_id, model=CarCategory)


async def get_car_depend(car_id: int = Query(None)) -> Car | None:
    return await model_getter(pk=car_id, model=Car)


async def get_payment_method_depend(payment_method_id: int = Query(None)) -> PaymentMethod | None:
    return await model_getter(pk=payment_method_id, model=PaymentMethod)


@dataclass
class RenderedServicesInfo:
    category: CarCategory
    service: Service
    payment_method: PaymentMethod
    car: Car


async def get_rendered_services_depend(
        category: CarCategory | None = Depends(get_category_depend),
        service: Service | None = Depends(get_service_depend),
        payment_method: PaymentMethod | None = Depends(get_payment_method_depend),
        car: Car | None = Depends(get_car_depend)
):
    return RenderedServicesInfo(
        category=category,
        service=service,
        payment_method=payment_method,
        car=car
    )
