from db.models import Car


async def get_car_value(value: str):
    return [item[value] for item in (await Car.all().values(value))]
