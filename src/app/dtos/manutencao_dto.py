from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from src.app.models.manutencao import Manutencao


class ManutencaoDTO(BaseModel):
    id: Optional[str] = None
    data_manutencao: datetime
    descricao: str
    custo : float
    observacao: str
    

    @classmethod
    def from_model(cls, manutencao: Manutencao):
        return cls(
            id=str(manutencao.id),
            data_manutencao=manutencao.data_manutencao,
            descricao=manutencao.descricao,
            custo=manutencao.custo,
            observacao=manutencao.observacao
        )
        
    def to_model(self) -> Manutencao:
        return Manutencao(
            id=self.id,
            data_manutencao=self.data_manutencao,
            descricao=self.descricao,
            custo=self.custo,
            observacao=self.observacao
        )
        
        