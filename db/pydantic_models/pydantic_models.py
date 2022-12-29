from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel

from db.models import (
    Service,
    User,
    ServiceCategoryPrice,
    CarCategory,
    Car,
    PaymentMethod, RenderedService,
)
from tortoise import Tortoise

Tortoise.init_models(["db.models"], "models")

Service_pydantic = pydantic_model_creator(Service, name="Service")
ServiceIn_pydantic = pydantic_model_creator(
    Service, name="ServiceIn", exclude_readonly=True
)
ServicePagination_pydantic = pydantic_model_creator(
    Service,
    name="ServicePagination",
    exclude=("prices", "rendered_services"),
    computed=("max_default_price", "min_default_price"),
)


class CroppedPrices(PydanticModel):
    category_id: int
    default_price: int

    class Config:
        orig_model = ServiceCategoryPrice


class ServiceCropped(ServiceIn_pydantic):
    id: int
    prices: list[CroppedPrices]


User_pydantic = pydantic_model_creator(User, name="User")
UserIn_pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
UserOut_pydantic = pydantic_model_creator(
    User, name="UserOut", exclude=("is_admin", "is_sadmin"), computed=("roles",)
)


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
    CarCategory,
    name="CarCategoryIn",
    exclude_readonly=True,
)
CarCategoryOut_pydantic = pydantic_model_creator(
    CarCategory, name="CarCategoryOut", exclude=("prices", "cars")
)

Car_pydantic = pydantic_model_creator(Car, name="Car")
CarIn_pydantic = pydantic_model_creator(
    Car, name="CarIn", exclude_readonly=True, exclude=("owner_id",)
)

CarOut_pydantic = pydantic_model_creator(
    Car, name="CarOut", exclude=("category",)
)


class CarOut(
    pydantic_model_creator(
        Car,
        name="_CarOut",
        exclude_readonly=True)
):
    id: int
    rendered_services: list[RenderedService]
    category_id: int

    class Config:
        arbitrary_types_allowed = True


CarPostOut_pydantic = pydantic_model_creator(
    Car, name="CarPostOut", exclude=("category.prices", "rendered_services")
)

PaymentMethod_pydantic = pydantic_model_creator(PaymentMethod, name="PaymentMethod")
PaymentMethodCropped_pydantic = pydantic_model_creator(
    PaymentMethod, name="PaymentMethodCropped", exclude=("rendered_services",)
)
PaymentMethodIn_pydantic = pydantic_model_creator(
    PaymentMethod, name="PaymentMethodIn", exclude_readonly=True
)


class BoundServiceCategory(BaseModel):
    category_id: int
    service_id: int
    default_price: int


class AddServiceForm(ServiceIn_pydantic):
    prices: list[ServiceCategoryPriceInMultiple_pydantic] | None


class PaginationForm(BaseModel):
    q: str | None = None
    limit: int = 5
    page: int = 0


class PaginationModelOut(BaseModel):
    docs: list[dict]
    hasNext: bool
    hasPrev: bool
    totalPages: int
    totalDocs: int
