from fastapi import APIRouter, Depends

from app.auth import jwt_dependency
from app.dependencies import get_car_depend
from app.utils import (
    simple_object_creation,
    update_from_dict,
    delete_obj,
    get_paginated_items,
    get_car_values,
)
from db.models import Car
from db.pydantic_models import (
    CarIn_pydantic,
    CarOut,
    CarPostOut_pydantic, PaginationModelOut,
)

router = APIRouter(
    prefix="/cars",
    tags=["cars"],
    dependencies=[
        # Depends(jwt_dependency)
    ],
)


@router.get("", response_model=PaginationModelOut)
async def get_cars(q: str = None, limit: int = 5, page: int = 1):
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
    await car.fetch_related("rendered_services")
    return await CarOut.from_tortoise_orm(car)


@router.get("/brands")
async def get_car_brands():
    return list(set(await get_car_values(["brand"])))


@router.get("/models")
async def get_car_models():
    return list(set(await get_car_values(["model"])))


@router.get("/numberplates")
async def get_car_numberplates():
    return await get_car_values(["id", "numberplate"])


@router.get("/check_numberplate")
async def check_car_numberplate(numberplate: str):
    return {"unique": not (await Car.exists(numberplate=numberplate))}


@router.post("")
async def add_car(car_form: CarIn_pydantic):
    car = await simple_object_creation(
        model=Car, creation_field="numberplate", data_dict=car_form.dict()
    )
    await car.fetch_related("rendered_services")
    return await CarPostOut_pydantic.from_tortoise_orm(car)


@router.patch("/{car_id:int}")
async def update_car(updated_car: CarIn_pydantic, car_id: int):
    updated_car_pydantic = await update_from_dict(
        model=Car,
        pydantic_model=CarOut,
        update_dict=updated_car.dict(),
        obj_pk=car_id,
        fetch_related=["rendered_services"]
    )
    return updated_car_pydantic


@router.delete("/{car_id:int}")
async def delete_car(car=Depends(get_car_depend)):
    return await delete_obj(car, CarOut)
