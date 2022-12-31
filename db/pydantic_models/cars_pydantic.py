from pydantic import BaseModel


class CheckCarNumberplateForm(BaseModel):
    numberplate: str
