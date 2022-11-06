from fastapi import APIRouter, Depends

from app.auth import jwt_dependency
from app.dependencies import get_car_depend
from app.utils import simple_object_creation
from db.models import Car
from db.pydantic_models import Car_pydantic, CarIn_pydantic

router = APIRouter(
    prefix="/cars",
    tags=["cars"],
    dependencies=[
        # Depends(jwt_dependency)
    ],
)


@router.get("")
async def get_cars():
    cars = await Car.all()
    return {"cars": await Car_pydantic.from_tortoise_orm(cars)}


@router.get("/{car_id:int}")
async def get_car(car=Depends(get_car_depend)):
    return {**(await Car_pydantic.from_tortoise_orm(car)).dict()}


@router.post("")
async def add_car(car_form: CarIn_pydantic):
    car = await simple_object_creation(
        model=Car, creation_field="numberplate", data_dict=car_form.dict()
    )
    return {**(await Car_pydantic.from_tortoise_orm(car)).dict()}
