from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_409_CONFLICT
from tortoise.exceptions import OperationalError

from app.auth import jwt_dependency
from app.dependencies import get_service_depend
from db.models import Service, ServiceCategoryPrice
from db.pydantic_models import (
    Service_pydantic,
    AddServiceForm,
    BoundServiceCategory,
    ServiceCategoryPrice_pydantic,
    PaginationForm,
)
from app.utils import (
    get_paginated_items,
    bound_service_and_category,
    update_service_from_dict,
)

router = APIRouter(
    prefix="/services",
    tags=["services"],
    dependencies=[
        # Depends(jwt_dependency)
    ],
)


@router.get("")
async def get_services(form=PaginationForm):
    data = await get_paginated_items(
        form.q, form.page, form.limit, Service_pydantic, Service, "title"
    )
    return data


@router.get("/{service_id:int}")
async def get_service(service: Service = Depends(get_service_depend)):
    return {**(await Service_pydantic.from_tortoise_orm(service)).dict()}


@router.post("/")
async def add_service(service_form: AddServiceForm):
    service_dict = service_form.dict()
    service, is_created = await Service.get_or_create(
        title=service_dict["title"], defaults={"self_cost": service_dict["self_cost"]}
    )
    if not is_created:
        raise HTTPException(HTTP_409_CONFLICT, detail="Already Exist")
    for price in service_dict["prices"]:
        await bound_service_and_category(
            service=service,
            category_id=price["category_id"],
            default_price=price["default_price"],
        )
    service = await Service.get(pk=service.id)
    return {**(await Service_pydantic.from_tortoise_orm(service)).dict()}


@router.delete("/{service_id:int}")
async def delete_service(service: Service = Depends(get_service_depend)):
    try:
        await service.delete()
    except OperationalError:
        raise HTTPException(
            HTTP_500_INTERNAL_SERVER_ERROR, detail="Not deleted due to internal error"
        )
    return {"service": await Service_pydantic.from_tortoise_orm(service)}


@router.patch("/{service_id:int}")
async def update_service(updated_service: AddServiceForm, service_id: int):
    updated_service_pydantic = await update_service_from_dict(
        update_dict=updated_service.dict(), service_id=service_id
    )
    return {**updated_service_pydantic.dict()}


@router.post("/bound_price")
async def bound_service_category(bound_form: BoundServiceCategory):
    bounded_info, is_created = await ServiceCategoryPrice.get_or_create(
        service__id=bound_form.service_id,
        category__id=bound_form.category_id,
        defaults={"default_price": bound_form.default_price},
    )
    if not is_created:
        raise HTTPException(HTTP_409_CONFLICT, detail="Already Exist")
    return {**(await ServiceCategoryPrice_pydantic.from_tortoise_orm(bounded_info))}
