from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class VeiculoManutencao(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    veiculo_id: ObjectId = Field(...)
    manutencao_id: ObjectId = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True