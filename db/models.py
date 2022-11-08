import datetime

from tortoise.exceptions import NoValuesFetched
from tortoise.models import Model
from tortoise import fields


class User(Model):
    id = fields.IntField(pk=True)
    tg_id = fields.BigIntField(null=False, unique=True)
    name = fields.CharField(max_length=255, null=False)
    username = fields.CharField(max_length=255)
    created_time = fields.DatetimeField(null=False, default=datetime.datetime.now)
    is_admin = fields.BooleanField(default=False)

    def __str__(self):
        return f"User({self.name=}, {self.tg_id=})"


class CarCategory(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"CarCategory({self.title=})"


class Car(Model):
    id = fields.IntField(pk=True)
    brand = fields.CharField(max_length=30, null=True)
    model = fields.CharField(max_length=50, null=True)
    numberplate = fields.CharField(max_length=50, null=False)
    owner = fields.ForeignKeyField(
        "models.User", related_name="cars", null=True, on_delete=fields.SET_NULL
    )
    category = fields.ForeignKeyField(
        "models.CarCategory", related_name="cars", null=True, on_delete=fields.SET_NULL
    )

    def __str__(self):
        return f"Car({self.brand=}, {self.model=}, {self.numberplate=})"


class ServiceCategoryPrice(Model):
    id = fields.IntField(pk=True)
    category = fields.ForeignKeyField(
        "models.CarCategory", related_name="prices", on_delete=fields.CASCADE
    )
    service = fields.ForeignKeyField(
        "models.Service", related_name="prices", on_delete=fields.CASCADE
    )
    default_price = fields.IntField()

    def __str__(self):
        return f"ServiceCategoryPrice({self.category=}, {self.service=}, {self.default_price=})"


class Service(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255, null=False, unique=True)
    self_cost = fields.IntField()
    prices: fields.ReverseRelation["ServiceCategoryPrice"]
    rendered_services: fields.ReverseRelation["RenderedService"]

    def max_default_price(self) -> int:
        try:
            if len(self.prices) > 0:
                return max([price.default_price for price in self.prices])
            else:
                return 0
        except NoValuesFetched:
            return 0

    def min_default_price(self) -> int:
        try:
            if len(self.prices) > 0:
                return min([price.default_price for price in self.prices])
            else:
                return 0
        except NoValuesFetched:
            return 0

    def __str__(self):
        return f"Service({self.title=}, {self.self_cost})"


class RenderedService(Model):
    id = fields.IntField(pk=True)
    car = fields.ForeignKeyField("models.Car", related_name="rendered_services")
    service = fields.ForeignKeyField("models.Service", related_name="rendered_services")
    price = fields.IntField(null=False)
    comment = fields.TextField(null=True)
    created_time = fields.DatetimeField(null=False, default=datetime.datetime.now)

    def __str__(self):
        return f"RenderedService({self.car=}, {self.price=}, {self.service=})"


class SupremeAdmin(Model):
    id = fields.IntField(pk=True)
    tg_id = fields.BigIntField(null=False)

    def __str__(self):
        return f"SupremeAdmin({self.tg_id=})"
