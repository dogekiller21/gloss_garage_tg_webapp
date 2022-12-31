from pydantic import BaseModel


class CheckServiceTitleForm(BaseModel):
    title: str
