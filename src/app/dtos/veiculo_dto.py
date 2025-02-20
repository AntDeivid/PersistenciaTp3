from pydantic import BaseModel
from typing_extensions import Optional

from src.app.models.veiculo import Veiculo


class VeiculoDTO(BaseModel):
    id: Optional[str] = None
    modelo: str
    marca: str
    placa: str
    ano: int

    @classmethod
    def from_model(cls, veiculo):
        return cls(
            id=str(veiculo.id),
            modelo=veiculo.modelo,
            marca=veiculo.marca,
            placa=veiculo.placa,
            ano=veiculo.ano
        )

    @classmethod
    def to_model(cls) -> Veiculo:
        return Veiculo(
            modelo=cls.modelo,
            marca=cls.marca,
            placa=cls.placa,
            ano=cls.ano
        )