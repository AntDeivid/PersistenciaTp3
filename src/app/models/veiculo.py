from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class Veiculo(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    modelo: str = Field(...)
    marca: str = Field(...)
    placa: str = Field(...)
    ano: int = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True