from pydantic import BaseModel


class CheckCarCategoryTitleForm(BaseModel):
    title: str
