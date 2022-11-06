from fastapi import HTTPException, Depends
from starlette.status import HTTP_404_NOT_FOUND

from app.auth import JWTBearer
from db.models import Service, CarCategory, User

jwt_dependency = JWTBearer()


async def admin_depend(payload=Depends(jwt_dependency)):
    tg_id = payload["tg_id"]
    user = await User.get_or_none(tg_id=tg_id)
    if user is None:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="User not found")


async def get_service_depend(service_id: int) -> Service:
    service = await Service.get_or_none(pk=service_id)
    if service is None:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Does not exist")
    return service


async def get_category_depend(category_id: int) -> CarCategory:
    category = await CarCategory.get_or_none(pk=category_id)
    if category is None:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="Does not exist")
    return category
