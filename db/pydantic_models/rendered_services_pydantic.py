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


class RenderedServiceOut(RenderedServiceROnly_pydantic):
    id: int
