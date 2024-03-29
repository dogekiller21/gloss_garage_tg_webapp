import math
from typing import Any, Union

from fastapi import HTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from tortoise import Model
from tortoise.contrib.pydantic import PydanticModel
from tortoise.exceptions import OperationalError
from tortoise.expressions import Q

from db.pydantic_models import PaginationModelOut


async def get_paginated_items(
    page: int | None,
    limit: int | None,
    pydantic_model: PydanticModel | Any,
    tortoise_model: Union[Model, Any],
    q: str | None = None,
    search_rows: list[str] = None,
    fetch_related: list[str] = None,
    additional_query: dict[str, Any] = None,
):

    if (limit is not None) and (page is not None) and (limit <= 0 or page <= 0):
        raise HTTPException(
            HTTP_400_BAD_REQUEST, detail="Limit and page must be positive"
        )
    if (limit is not None and page is None) or (limit is None and page is not None):
        raise HTTPException(
            HTTP_400_BAD_REQUEST, detail="Limit and page must be in a pair. They are so pretty together"
        )
    if (q is None or not q) or (search_rows is None and additional_query is None):
        items_tortoise = await tortoise_model.all().order_by("id")
    else:
        if search_rows is not None:
            expressions = [Q(**{f"{row}__icontains": q}) for row in search_rows]
            tortoise_expression = Q(*expressions, join_type="OR")
        else:
            tortoise_expression = None
        if additional_query is not None:
            additional_expressions = [
                Q(**{item[0]: item[1] for item in additional_query.items() if item[1] is not None})
            ]
            if search_rows is not None:
                final_expressions = Q(tortoise_expression, *additional_expressions, join_type="AND")
            else:
                final_expressions = Q(*additional_expressions, join_type="AND")
        else:
            final_expressions = tortoise_expression
        items_tortoise = await tortoise_model.filter(final_expressions).order_by("id")
    if fetch_related is not None:
        await tortoise_model.fetch_for_list(items_tortoise, *fetch_related)
    items = [await pydantic_model.from_tortoise_orm(item) for item in items_tortoise]
    if limit is None and page is None:
        return PaginationModelOut(
            docs=items,
            hasNext=False,
            hasPrev=False,
            totalPages=0,
            totalDocs=len(items)
        )
    offset = (page - 1) * limit
    query_limit = offset + limit

    if (offset > len(items) - 1) and (len(items) >= limit) and (len(items) != 0):
        return_items = list()
    else:
        return_items = items[offset:query_limit]
    has_prev = offset != 0
    has_next = query_limit < len(items)
    max_page = math.ceil(len(items) / limit)
    # docs потому что у Вадика плагин в бошке застрял (нормальное название - items)
    return PaginationModelOut(
        docs=return_items,
        hasNext=has_prev,
        hasPrev=has_next,
        totalPages=max_page,
        totalDocs=len(items)
    )


async def update_from_dict(
    model: Model | Any,
    pydantic_model: PydanticModel | Any | None,
    update_dict: dict,
    obj_pk: int | Any,
    return_model: bool = False,
    fetch_related: list = None,
):
    if pydantic_model is None and not return_model:
        raise ValueError("pydantic_model must not be None if return_model set to False")
    item = await model.get_or_none(pk=obj_pk)
    if item is None:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Does not exist")
    updated_item = item.update_from_dict(update_dict)
    await updated_item.save(force_update=True)
    if return_model:
        return updated_item
    if fetch_related is not None:
        await updated_item.fetch_related(*fetch_related)
    return await pydantic_model.from_tortoise_orm(updated_item)


async def simple_object_creation(model, creation_field: str, data_dict: dict):
    primary_field = data_dict.pop(creation_field)
    obj, is_created = await model.get_or_create(
        **{creation_field: primary_field}, defaults={**data_dict}
    )
    if not is_created:
        if not is_created:
            raise HTTPException(HTTP_409_CONFLICT, detail="Already Exist")
    return obj


async def delete_obj(obj: Model | Any, pydantic_model: PydanticModel | Any) -> dict:
    try:
        await obj.delete()
    except OperationalError:
        raise HTTPException(
            HTTP_500_INTERNAL_SERVER_ERROR, detail="Not deleted due to internal error"
        )
    return {**(await pydantic_model.from_tortoise_orm(obj)).dict()}
