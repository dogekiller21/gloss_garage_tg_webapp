from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from db.models import Service, User, ServiceCategoryPrice, CarCategory
from tortoise import Tortoise

Tortoise.init_models(["db.models"], "models")

Service_pydantic = pydantic_model_creator(Service, name="Service")
ServiceIn_pydantic = pydantic_model_creator(
    Service, name="ServiceIn", exclude_readonly=True
)

User_pydantic = pydantic_model_creator(User, name="User")
UserIn_pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)

ServiceCategoryPrice_pydantic = pydantic_model_creator(
    ServiceCategoryPrice, name="ServiceCategoryPrice", exclude=("service",)
)
ServiceCategoryPriceIn_pydantic = pydantic_model_creator(
    ServiceCategoryPrice, name="ServiceCategoryPriceIn", exclude_readonly=True
)
ServiceCategoryPriceInMultiple_pydantic = pydantic_model_creator(
    ServiceCategoryPrice,
    name="ServiceCategoryPriceInMultiple",
    exclude_readonly=True,
    exclude=("service_id",),
)

CarCategory_pydantic = pydantic_model_creator(CarCategory, name="CarCategory")
CarCategoryIn_pydantic = pydantic_model_creator(
    CarCategory, name="CarCategoryIn", exclude_readonly=True,
)
CarCategoryOut_pydantic = pydantic_model_creator(
    CarCategory, name="CarCategoryOut", exclude=("prices", "cars")
)


class BoundServiceCategory(BaseModel):
    category_id: int
    service_id: int
    default_price: int


class AddServiceForm(ServiceIn_pydantic):
    prices: list[ServiceCategoryPriceInMultiple_pydantic] | None
