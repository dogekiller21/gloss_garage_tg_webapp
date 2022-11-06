import math
from typing import Any, Union

from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from tortoise import Model
from tortoise.contrib.pydantic import PydanticModel

from db.models import Service, CarCategory, ServiceCategoryPrice
from db.pydantic_models import Service_pydantic, ServiceCategoryPrice_pydantic


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


async def get_paginated_items(
    q: str | None,
    page: int,
    limit: int,
    pydantic_model: PydanticModel,
    tortoise_model: Union[Model, Any],
    search_row: str = "title",
):
    if limit <= 0 or page < 0:
        raise HTTPException(
            HTTP_400_BAD_REQUEST, detail="Limit and page must be positive"
        )
    if q is None or not q:
        items = await pydantic_model.from_queryset(tortoise_model.all().order_by("id"))
    else:
        items = await pydantic_model.from_queryset(
            tortoise_model.filter(**{f"{search_row}__icontains": q}).order_by("id")
        )
    offset = page * limit
    query_limit = offset + limit
    if (offset > len(items) - 1) and (len(items) >= limit) and (len(items) != 0):
        raise HTTPException(HTTP_400_BAD_REQUEST, detail="Too much offset")
    return_items = items[offset:query_limit]

    has_prev = offset != 0
    has_next = query_limit < len(items)
    max_page = math.ceil(len(items) / limit)
    # docs потому что у Вадика плагин в бошке застрял (нормальное название - items)
    return {
        "docs": return_items,
        "hasPrev": has_prev,
        "hasNext": has_next,
        "totalPages": max_page,
    }


async def update_from_dict(
    model: Model | Any,
    pydantic_model: PydanticModel | None,
    update_dict: dict,
    obj_pk: int | Any,
    return_model: bool = False,
):
    if pydantic_model is None and not return_model:
        raise ValueError("update_dict must not be None if return_model set to False")
    item = await model.get_or_none(pk=obj_pk)
    if item is None:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Does not exist")
    updated_item = item.update_from_dict(update_dict)
    await updated_item.save(force_update=True)
    if return_model:
        return updated_item
    return await pydantic_model.from_tortoise_orm(updated_item)


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


async def simple_object_creation(model, creation_field: str, data_dict: dict):
    primary_field = data_dict.pop(creation_field)
    obj, is_created = await model.get_or_create(
        **{creation_field: primary_field}, defaults={**data_dict}
    )
    if not is_created:
        if not is_created:
            raise HTTPException(HTTP_409_CONFLICT, detail="Already Exist")
    return obj
