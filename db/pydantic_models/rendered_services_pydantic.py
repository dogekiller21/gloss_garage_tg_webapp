from typing import Optional

from pydantic import Field
from tortoise.contrib.pydantic import pydantic_model_creator
from typing_extensions import Annotated

from db.models import RenderedService, Car

RenderedService_pydantic = pydantic_model_creator(
    RenderedService, name="RenderedService"
)

RenderedServiceROnly_pydantic = pydantic_model_creator(
    RenderedService,
    name="RenderedServiceROnly",
    exclude_readonly=True,
)


class RenderedServiceIn(pydantic_model_creator(
        RenderedService,
        name="__RenderedServiceIn",
        exclude_readonly=True,
        exclude=("car",),
    )):
    car_id: Annotated[int, Field(title="Car id")] = None
    car_numberplate: Annotated[str, Field(title="Car numberplate")] = None
    car_model: Annotated[str, Field(title="Car model")] = None
    car_brand: Annotated[str, Field(title="Car brand")] = None


class RenderedServiceOut(RenderedServiceROnly_pydantic):
    id: int
