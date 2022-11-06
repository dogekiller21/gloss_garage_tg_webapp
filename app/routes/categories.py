from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_409_CONFLICT

from app.dependencies import get_category_depend, jwt_dependency

from db.models import CarCategory
from db.pydantic_models import CarCategoryIn_pydantic, CarCategoryOut_pydantic
from db.utils import get_paginated_items, update_from_dict

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    dependencies=[
        # Depends(jwt_dependency)
    ]
)


@router.get("")
async def get_categories(q: str | None = None, page: int = 0, limit: int = 5):
    data = await get_paginated_items(
        q, page, limit, CarCategoryOut_pydantic, CarCategory, "title"
    )
    return data


@router.get("/{category_id:int}")
async def get_category(category: CarCategory = Depends(get_category_depend)):
    return {**(await CarCategoryOut_pydantic.from_tortoise_orm(category)).dict()}


@router.post("/")
async def add_category(category_form: CarCategoryIn_pydantic):
    category, is_created = await CarCategory.get_or_create(
        title=category_form.dict()["title"]
    )
    if not is_created:
        raise HTTPException(HTTP_409_CONFLICT, detail="Already Exist")
    return {**(await CarCategoryOut_pydantic.from_tortoise_orm(category)).dict()}


@router.patch("/{category_id:int}")
async def update_category(updated_category: CarCategoryIn_pydantic, category_id: int):
    updated_category_pydantic = await update_from_dict(
        model=CarCategory,
        pydantic_model=CarCategoryOut_pydantic,
        update_dict=updated_category.dict(),
        obj_pk=category_id,
    )
    return {**updated_category_pydantic.dict()}
