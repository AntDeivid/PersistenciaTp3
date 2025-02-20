from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from src.app.models.manutencao import Manutencao

class ManutencaoDTO(BaseModel):
    id: Optional[str] = None
    data: datetime
    tipo_manutencao: str
    custo: float
    observacao: str

    @classmethod
    def from_model(cls, manutencao: Manutencao):
        return cls(
            id=str(manutencao.id) if manutencao.id else None,
            data=manutencao.data,
            tipo_manutencao=manutencao.tipo_manutencao,
            custo=manutencao.custo,
            observacao=manutencao.observacao
        )
        
    def to_model(self) -> Manutencao:
        return Manutencao(
            id=self.id,
            data=self.data,
            tipo_manutencao=self.tipo_manutencao,
            custo=self.custo,
            observacao=self.observacao
        )