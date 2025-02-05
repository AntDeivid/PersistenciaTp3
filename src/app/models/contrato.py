from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Contrato(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    usuario_id: str = Field(...)
    veiculo_id: str = Field(...)
    pagamento_id: Optional[str] = Field(default=None)
    data_inicio: datetime = Field(...)
    data_fim: datetime = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}