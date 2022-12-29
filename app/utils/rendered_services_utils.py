from app.utils import get_paginated_items
from db.models import CarCategory, Car, PaymentMethod, Service, RenderedService
from db.pydantic_models import RenderedServiceOut


async def paginate_rendered_services(
        category: CarCategory | None = None,
        service: Service | None = None,
        payment_method: PaymentMethod | None = None,
        car: Car | None = None,
        limit: int | None = None,
        page: int | None = None,
):
    items = await get_paginated_items(
        page=page,
        limit=limit,
        pydantic_model=RenderedServiceOut,
        tortoise_model=RenderedService,
        additional_query={
            "category": category,
            "service": service,
            "payment_method": payment_method,
            "car": car
        }
    )
    return items
