from typing import Optional

from pydantic import BaseModel, Field


class Usuario(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    nome: str = Field(...)
    email: str = Field(...)
    celular: Optional[str] = Field(default=None)
    cpf: str = Field(...)

    class Config:
        allow_population_by_field_name = True