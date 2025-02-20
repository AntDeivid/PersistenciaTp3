from typing import Optional

from bson import ObjectId
from pydantic import BaseModel

from src.app.models.veiculo_manutencao import VeiculoManutencao


class VeiculoManutencaoDTO(BaseModel):
    id: Optional[str] = None
    veiculo_id: str
    manutencao_id: str

    @classmethod
    def from_model(cls, veiculo_manutencao):
        return cls(
            id=str(veiculo_manutencao.id),
            veiculo_id=str(veiculo_manutencao.veiculo_id),
            manutencao_id=str(veiculo_manutencao.manutencao_id)
        )

    @classmethod
    def to_model(cls) -> VeiculoManutencao:
        return VeiculoManutencao(
            veiculo_id=ObjectId(cls.veiculo_id),
            manutencao_id=ObjectId(cls.manutencao_id)
        )