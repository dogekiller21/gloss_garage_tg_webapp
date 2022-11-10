from fastapi import APIRouter, Depends

from app.auth import jwt_dependency
from app.dependencies import get_car_depend
from app.utils import (
    simple_object_creation,
    update_from_dict,
    delete_obj,
    get_paginated_items, get_all_car_brands, get_all_car_models,
)
from db.models import Car
from db.pydantic_models import (
    CarIn_pydantic,
    CarOut_pydantic,
    CarPostOut_pydantic,
)

router = APIRouter(
    prefix="/cars",
    tags=["cars"],
    dependencies=[
        # Depends(jwt_dependency)
    ],
)


@router.get("")
async def get_cars(q: str = None, limit: int = 5, page: int = 0):
    data = await get_paginated_items(
        q=q,
        page=page,
        limit=limit,
        pydantic_model=CarPostOut_pydantic,
        tortoise_model=Car,
        search_rows=["numberplate", "model", "brand"],
    )
    return data


@router.get("/{car_id:int}")
async def get_car(car=Depends(get_car_depend)):
    return {**(await CarOut_pydantic.from_tortoise_orm(car)).dict()}


@router.get("/brands")
async def get_car_brands():
    return await get_all_car_brands()


@router.get("/models")
async def get_car_models():
    return await get_all_car_models()


@router.post("")
async def add_car(car_form: CarIn_pydantic):
    car = await simple_object_creation(
        model=Car, creation_field="numberplate", data_dict=car_form.dict()
    )
    return {**(await CarPostOut_pydantic.from_tortoise_orm(car)).dict()}


@router.patch("/{car_id:int}")
async def update_car(updated_car: CarIn_pydantic, car_id: int):
    updated_car_pydantic = await update_from_dict(
        model=Car,
        pydantic_model=CarOut_pydantic,
        update_dict=updated_car.dict(),
        obj_pk=car_id,
    )
    return {**updated_car_pydantic.dict()}


@router.delete("/{car_id:int}")
async def delete_car(car=Depends(get_car_depend)):
    return await delete_obj(car, CarOut_pydantic)
