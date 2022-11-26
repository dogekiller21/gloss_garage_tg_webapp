from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from app.utils.general import update_from_dict
from db.models import Service, ServiceCategoryPrice, CarCategory
from db.pydantic_models import Service_pydantic


async def bound_service_and_category(
    service: Service, category_id: int, default_price: int
):
    category = await CarCategory.get_or_none(pk=category_id)
    if category is None:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail="No such category")
    bounded_price, _ = await ServiceCategoryPrice.update_or_create(
        service=service,
        category_id=category_id,
        defaults={"default_price": default_price},
    )
    return bounded_price


async def update_service_category_price(
    service_id: int, category_id: int, default_price: int
):
    item, is_created = await ServiceCategoryPrice.get_or_create(
        service_id=service_id,
        category_id=category_id,
        defaults={"default_price": default_price},
    )
    if is_created:
        return
    item.default_price = default_price
    await item.save(force_update=True)


async def update_service_from_dict(
    update_dict: dict, service_id: int, return_model: bool = False
):
    service = await Service.get_or_none(pk=service_id)
    if service is None:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail="Does not exist")
    prices = update_dict.pop("prices")
    updated_service = await update_from_dict(
        model=Service,
        pydantic_model=None,
        update_dict=update_dict,
        obj_pk=service_id,
        return_model=True,
    )
    service_prices = await ServiceCategoryPrice.filter(service_id=service_id)
    included_categories = [price["category_id"] for price in prices]
    services_to_delete = [
        item
        for item in service_prices
        if (await item.category).id not in included_categories
    ]
    for item in services_to_delete:
        await item.delete()
    for price_dict in prices:
        await update_service_category_price(**price_dict, service_id=updated_service.pk)
    fresh_service = await Service.get_or_none(pk=service_id)
    if return_model:
        return fresh_service
    return await Service_pydantic.from_tortoise_orm(fresh_service)
