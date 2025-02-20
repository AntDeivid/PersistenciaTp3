from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class Manutencao(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    data: datetime = Field(...)
    tipo_manutencao: str = Field(...)
    custo: float = Field(...)
    observacao: str = Field(...)

    class Config:
        allow_population_by_field_name = True