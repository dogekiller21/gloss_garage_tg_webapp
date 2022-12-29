from db.models import Car


async def get_car_values(values: list[str]):
    if len(values) != 1:
        return [{value: item[value] for value in values} for item in (await Car.all().values(*values))]
    return [item[values[0]] for item in (await Car.all().values(values[0]))]
