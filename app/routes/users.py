from fastapi import APIRouter, Depends

from app.dependencies import jwt_dependency, user_depend, sadmin_depend
from db.models import User
from db.pydantic_models import User_pydantic, UserOut_pydantic

router = APIRouter(
    prefix="/users", tags=["users"], dependencies=[Depends(jwt_dependency)]
)


@router.get("", dependencies=[Depends(sadmin_depend)])
async def get_users():
    return await User_pydantic.from_queryset(User.all())


@router.get("/me")
async def get_current_user(current_user=Depends(user_depend)):
    return {**(await UserOut_pydantic.from_tortoise_orm(current_user)).dict()}
