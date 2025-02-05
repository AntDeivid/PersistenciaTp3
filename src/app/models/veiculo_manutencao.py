from typing import Optional

from pydantic import BaseModel, Field


class VeiculoManutencao(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    veiculo_id: str = Field(...)
    manutencao_id: str = Field(...)

    class Config:
        allow_population_by_field_name = True