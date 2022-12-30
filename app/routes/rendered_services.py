from fastapi import APIRouter, Depends, HTTPException, Body
from starlette.status import HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY

from app.auth import jwt_dependency
from app.dependencies import get_rendered_services_depend, RenderedServicesInfo
from db.models import Car, RenderedService

from db.pydantic_models import (
    RenderedService_pydantic, RenderedServiceROnly_pydantic,
)
from app.utils import get_paginated_items, update_from_dict, delete_obj, paginate_rendered_services

router = APIRouter(
    prefix="/rendered_services",
    tags=["rendered_services"],
    dependencies=[
        # Depends(jwt_dependency)
    ],
)


@router.get("")
async def get_rendered_services(
        limit: int = None,
        page: int = None,
        info: RenderedServicesInfo = Depends(get_rendered_services_depend),
):
    data = await paginate_rendered_services(
        service=info.service,
        category=info.category,
        payment_method=info.payment_method,
        car=info.car,
        limit=limit,
        page=page,
    )
    return data


@router.post("", response_model=RenderedService_pydantic)
async def add_rendered_service(form: RenderedServiceROnly_pydantic):
    if form.car_id is None and (form.car_model is None or form.car_brand is None or form.car_numberplate is None):
        raise HTTPException(
            HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Car model, brand and numberplate must not be None if car id is None",
        )

    if form.car_id is None:
        new_car, _ = await Car.get_or_create(
            numberplate=form.car_numberplate,
            defaults={
                "model": form.car_model,
                "brand": form.car_brand
            }
        )
        car_id = new_car.id
    else:
        car_id = form.car_id
    new_rendered_service = await RenderedService.create(
        car_id=car_id,
        service_id=form.service_id,
        price=form.price,
        comment=form.comment,
        payment_method_id=form.payment_method_id
    )
    return await RenderedService_pydantic.from_tortoise_orm(new_rendered_service)
