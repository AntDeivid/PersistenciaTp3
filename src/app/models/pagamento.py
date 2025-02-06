from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Pagamento(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    valor: float = Field(...)
    forma_pagamento: str = Field(...)
    vencimento: datetime = Field(...)
    pago: bool = Field(default=False)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}
        