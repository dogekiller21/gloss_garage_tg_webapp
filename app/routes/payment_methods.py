from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_409_CONFLICT

from app.auth import jwt_dependency
from app.dependencies import get_payment_method_depend
from db.models import PaymentMethod
from db.pydantic_models import (
    PaymentMethod_pydantic,
    PaymentMethodCropped_pydantic,
    PaymentMethodIn_pydantic,
)
from app.utils import (
    delete_obj,
    update_from_dict,
)

router = APIRouter(
    prefix="/payment_methods",
    tags=["payment_methods"],
    dependencies=[
        # Depends(jwt_dependency)
    ],
)


@router.get("")
async def get_payment_methods(exclude_services: bool = True):
    parse_pydantic_model = (
        PaymentMethodCropped_pydantic if exclude_services else PaymentMethod_pydantic
    )
    methods = [
        await parse_pydantic_model.from_tortoise_orm(method)
        for method in (await PaymentMethod.all().order_by("id"))
    ]
    return methods


@router.get("/{payment_method_id:int}")
async def get_payment_method(
    payment_method: PaymentMethod = Depends(get_payment_method_depend),
):
    return {**(await PaymentMethod_pydantic.from_tortoise_orm(payment_method)).dict()}


@router.post("")
async def add_payment_method(payment_method_form: PaymentMethodIn_pydantic):
    payment_method_dict = payment_method_form.dict()
    payment_method, is_created = await PaymentMethod.get_or_create(
        title=payment_method_dict["title"]
    )
    if not is_created:
        raise HTTPException(HTTP_409_CONFLICT, detail="Already Exist")
    return {
        **(await PaymentMethodCropped_pydantic.from_tortoise_orm(payment_method)).dict()
    }


@router.delete("/{payment_method_id:int}")
async def delete_payment_method(
    payment_method: PaymentMethod = Depends(get_payment_method_depend),
):
    return await delete_obj(obj=payment_method, pydantic_model=PaymentMethod_pydantic)


@router.patch("/{payment_method_id:int}")
async def update_service(
    payment_method_form: PaymentMethodIn_pydantic, payment_method_id: int
):
    updated_payment_method_pydantic = await update_from_dict(
        model=PaymentMethod,
        pydantic_model=PaymentMethod_pydantic,
        update_dict=payment_method_form.dict(),
        obj_pk=payment_method_id,
    )
    return {**updated_payment_method_pydantic.dict()}
